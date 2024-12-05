"""
This module contains utility functions related to Airflow tasks and workflows.

Functions:
- run_pipeline: Runs the specified pipeline based on the provided parameters.
- get_data: Retrieves data based on the specified parameters.
- preprocess_data: Preprocesses the data before further processing.
- post_process_data: Performs post-processing tasks on the data.
- validate_data: Validates the data to ensure quality and consistency.
"""

import os
# base_dir = os.getenv('OPENETL_HOME')
# sys.path.append(base_dir)
import uuid
import utils.connector_utils as con_utils
from utils.cache import *
from datetime import datetime, timedelta
import utils.spark_utils as sp_ut
from utils.enums import *
import utils.database_utils as database_utils

import logging

def create_airflow_dag(config):
    """Store pipeline configuration in .local/pipelines directory

    Args:
        config (string): Name of the pipeline

    Returns:
        tuple: Boolean, Config. True if stored
    """
    current_datetime = datetime.now()
    one_hour = timedelta(days=1)
    result_datetime = current_datetime - one_hour

    default_args = {
        'owner': 'admin',
        'depends_on_past': False,
        'start_date': result_datetime,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
    integration_name = config['integration_name']

    op_args = {
        "config": {"source": {"table": config["source_table"], "schema": config["source_schema"], "connection_type": config["source_type"],
                              "connection_name": config["source_connection_name"]},
                   "target": {"table": config["target_table"], "schema": config["target_schema"], "connection_type": config["target_type"],
                              "connection_name": config["target_connection_name"]}},
    }
    with open(f"{os.getcwd()}/utils/airflow_templates/full_load.py", 'r') as file:
        template = file.read()
    template = template.format(
        integration_name=integration_name, source_connection=op_args["config"]["source"],
        target_connection=op_args["config"]["target"],
        spark_config=config["spark_config"], hadoop_config=config["hadoop_config"], default_args=default_args)
    with open(f"{os.getenv('AIRFLOW_HOME')}/dags/{integration_name}.py", "w") as f:
        f.write(template)
    return True


def read_data(connection_type, table, schema, connection_name):
    """
    Reads data from a specified connection type.

    Args:
        connection_type (str): The type of connection to use. Valid values are "database" or "api".
        table (str): The name of the table to read from.
        schema (str): The schema of the table.
        connection_name (str): The name of the connection.

    Returns:
        Union[DataFrame]: If the connection type is "database", returns a Spark DataFrame containing the data. If the connection type is "api" returns a pandas DataFrame containing the data.

    Raises:
        ValueError: If the connection type is not "database" or "api".
    """
    if connection_type.lower() not in [ConnectionType.DATABASE.value, ConnectionType.API.value]:
        raise ValueError(f"Unsupported connection type: {connection_type}")

    if connection_type.lower() == ConnectionType.DATABASE.value:
        spark = sp_ut.SparkConnection(config)
        df = spark.read_via_spark()
        return df
    elif connection_type.lower() == ConnectionType.API.value:
        for data in con_utils.fetch_data_from_connector(connection_name, connection_type, table, schema):
            logging.info("######data######")
            logging.info(data)
            yield data


def extract_xcom_value(task_id, **context):
    # Extract XCom value
    xcom_value = context['task_instance'].xcom_pull(task_ids=task_id)

    # Do something with the XCom value
    print("Extracted XCom value:", xcom_value)
    return xcom_value


def run_pipeline(spark_config=None, hadoop_config=None, job_name=None, job_id=None, job_type=None,
                 source_table=None, source_schema=None, target_table=None, target_schema=None,
                 source_connection_details=None, target_connection_details=None):
    """
    A function that runs a pipeline with the specified configurations, particularly used in the airflow DAG to run a pipeline.

    Args:
        source_connection_type (str): The type of the source connection.
        source_table (str): The name of the source table.
        source_schema (str): The schema of the source table.
        source_connection_name (str): The name of the source connection.
        target_connection_type (str): The type of the target connection.
        target_connection_config (dict): The configuration details of the target connection.
        spark_config (dict, optional): The Spark configuration. Defaults to None.
        hadoop_config (dict, optional): The Hadoop configuration. Defaults to None.
        mapping (dict, optional): The mapping details. Defaults to None.
        integration_name (str, optional): The name of the integration. Defaults to None.

    Raises:
        Exception: If no data is found in the source table.
        NotImplementedError: If the target connection type is API.
    """

    logging.info("RUNNING PIPELINE")
    batch_id = str(uuid.uuid4())
    logging.info(f"Batch ID: {batch_id}")

    if target_connection_type.lower() == ConnectionType.DATABASE.value:
        connector_details = con_utils.get_created_connections("database",
                                                              connection_name=target_connection_config['connection_name'])[0]
        engine = con_utils.get_db_connector_engine(
            connector_details['connector_name'])
        connection_credentials = connector_details['connection_credentials']

        jar = jdbc_database_jars[engine]
        driver = jdbc_engine_drivers[engine]
        connection_details = {key.upper(): value for key,
                              value in connection_credentials.items()}
        con_string = jdbc_connection_strings[engine].format(
            **connection_details)

        schema_ops = database_utils.DatabaseUtils(
            engine=engine, **connection_credentials)
        schema_ops.create_batch_table()

        schema_ops.insert_openetl_batch(batch_id=batch_id, start_date=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), batch_type="full", batch_status="in progress", integration_name=integration_name)

        # df = schema_ops.cast_columns(df)
        # df = schema_ops.fill_na_based_on_dtype(df)

        # created, message = schema_ops.create_table(
        #     target_connection_config['table'], df)
        # if not created:
        #     raise Exception(message)
        logging.info("PRINTING OUT JARS")
        logging.info(jar)
        spark_class = sp_ut.SparkConnection(spark_configuration=spark_config,
                                            hadoop_configuration=hadoop_config, jar=jar, connection_string=con_string)
        spark_session = spark_class.initializeSpark()
        for df in read_data(source_connection_type, source_table,
                            source_schema, source_connection_name):

            logging.info("priniting out dataframe details.")
            logging.info(df.head(2))
            logging.info(df.dtypes)
            rows = df.shape[0]
            if rows == 0:
                logging.exception(df)
                raise Exception("No data found in source table")

            df = df.rename(columns=lambda x: x.replace('.', '_'))
            df = df.astype(str)

            df = spark_session.createDataFrame(df)
            # df = schema_ops.match_pandas_schema_to_spark(df)
            if spark_class.write_via_spark(
                    df, conn_string=con_string, table=target_connection_config['table'], driver=driver):
                rows = df.count()
                schema_ops.update_openetl_batch(batch_id=batch_id, batch_status="completed", end_date=datetime.now(
                ).strftime("%Y-%m-%d %H:%M:%S"), rows_count=rows)

        logging.info("FINISHED PIPELINE")
        logging.info("DISPOSING ENGINES")
        spark_class.__dispose__()
        schema_ops.__dispose__()

    elif target_connection_type.lower() == ConnectionType.API.value:
        raise NotImplementedError("API target connection not implemented")

