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
import sys
# base_dir = os.getenv('OPENETL_HOME')
# sys.path.append(base_dir)
import uuid

import pandas as pd

import openetl_utils.connector_utils as con_utils
from openetl_utils.__migrations__.batch import OpenETLBatch
from openetl_utils.cache import *
from datetime import datetime, timedelta
import openetl_utils.spark_utils as sp_ut
from openetl_utils.enums import *
import openetl_utils.database_utils as database_utils
from pyspark.sql import functions as F
from pyspark.sql.window import Window


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
        "config": {"source": {"table": config["source_table"], "schema": config["source_schema"],
                              "connection_type": config["source_type"],
                              "connection_name": config["source_connection_name"]},
                   "target": {"table": config["target_table"], "schema": config["target_schema"],
                              "connection_type": config["target_type"],
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


def read_data(connector_name, auth_values, auth_type, table, connection_type, schema="public", config={},
              batch_size=100000, logger=None):
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
    main_df = pd.DataFrame()  # Initialize an empty DataFrame
    if connection_type.lower() not in [ConnectionType.DATABASE.value, ConnectionType.API.value]:
        raise ValueError(f"Unsupported connection type: {connection_type}")

    elif connection_type.lower() == ConnectionType.API.value:
        for data in con_utils.fetch_data_from_connector(connector_name, auth_values, auth_type, table, connection_type,
                                                        schema="public"):
            logger.info("######data######")
            logger.info(data)
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Fetched data must be a pandas DataFrame")

            # Append data to main_df
            main_df = pd.concat([main_df, data], ignore_index=True)

            if len(main_df) >= batch_size:
                yield main_df
                main_df = pd.DataFrame()  # Reset

        yield main_df


def extract_xcom_value(task_id, **context):
    # Extract XCom value
    xcom_value = context['task_instance'].xcom_pull(task_ids=task_id)

    # Do something with the XCom value
    print("Extracted XCom value:", xcom_value)
    return xcom_value


def run_pipeline(spark_config=None, hadoop_config=None, job_name=None, job_id=None, job_type=None,
                 source_table=None, source_schema=None, target_table=None, target_schema=None,
                 source_connection_details=None, target_connection_details=None, batch_size=100000, logger=None):
    """
    A function that runs a pipeline with the specified configurations, particularly used in the airflow DAG to run a pipeline.

    Args:
        logger:
        target_schema:
        job_type:
        job_id:
        job_name:
        target_table:
        source_connection_details:
        target_connection_details:
        batch_size:
        source_table (str): The name of the source table.
        source_schema (str): The schema of the source table.
        spark_config (dict, optional): The Spark configuration. Defaults to None.
        hadoop_config (dict, optional): The Hadoop configuration. Defaults to None.

    Raises:
        Exception: If no data is found in the source table.
        NotImplementedError: If the target connection type is API.
    """
    global row_count
    exception = None
    run_status = None
    row_count = 0
    try:

        logger.info("RUNNING PIPELINE")

        target_credentials = target_connection_details['connection_credentials']
        source_credentials = source_connection_details['connection_credentials']


        if target_connection_details['connection_type'].lower() == ConnectionType.DATABASE.value:

            engine = con_utils.get_connector_engine(connector_name=target_connection_details['connector_name'])

            jar = jdbc_database_jars[engine]
            driver = jdbc_engine_drivers[engine]
            connection_details = {key.upper(): value for key,
            value in target_credentials.items()}
            con_string = jdbc_connection_strings[engine].format(
                **connection_details)

            db = database_utils.DatabaseUtils(
                engine=engine, **target_credentials)
            db.create_table_from_base(target_schema=target_schema, base=OpenETLBatch)

            logger.info("PRINTING OUT JARS")
            logger.info(jar)
            spark_class = sp_ut.SparkConnection(spark_configuration=spark_config,
                                                hadoop_configuration=hadoop_config, jar=jar,
                                                connection_string=con_string)
            spark_session = spark_class.initializeSpark()
            spark_config["spark.app.name"] = spark_config[
                                                 "spark.app.name"] + f"_read_source_table{source_table}"
            if source_connection_details["connection_type"].lower() == ConnectionType.DATABASE.value:

                connection_details_upper = {key.upper(): value for key, value in connection_details.items()}
                spark_conn_url = {"url": jdbc_connection_strings[engine].format(**connection_details_upper),
                                  "dbtable": source_table,
                                  "driver": jdbc_engine_drivers[engine]}

                for df in spark_class.read_via_spark(spark_conn_url):

                    if not df.empty:
                        df_count = df.count()
                        row_count = row_count + df_count
                        run_pipeline_target(df=df, integration_id=job_id, spark_class=spark_class, con_string=con_string,
                                            target_table=target_table, job_id=job_id, job_name=job_name, driver=driver,
                                            spark_session=spark_session, db_class=db, logger=logger, batch_size=batch_size)
            else:
                for df in read_data(connector_name=source_connection_details['connector_name'],
                                    auth_values=source_credentials,
                                    auth_type=source_connection_details['auth_type'],
                                    table=source_table,
                                    connection_type=source_connection_details['connection_type'],
                                    schema=source_schema,
                                    batch_size=batch_size,
                                    logger=logger):

                    if not df.empty:
                        df = db.fill_na_based_on_dtype(df)
                        logger.info(df)
                        df = spark_session.createDataFrame(df)
                        df_count = df.count()
                        row_count= row_count + df_count
                        run_pipeline_target(df=df, integration_id=job_id, spark_class=spark_class, con_string=con_string,
                                            target_table=target_table, job_id=job_id, job_name=job_name, driver=driver,
                                            spark_session=spark_session, db_class=db, logger=logger, batch_size=batch_size)

            run_status = RunStatus.SUCCESS

            logger.info("FINISHED PIPELINE")
            logger.info("DISPOSING ENGINES")
            spark_class.__dispose__()
            db.__dispose__()

        elif target_connection_details['connection_type'].lower() == ConnectionType.API.value:
            raise NotImplementedError("API target connection not implemented")
    except Exception as e:
        exception = str(e)
        logger.error(e)
        run_status = RunStatus.FAILED
        row_count = 0
    finally:
        update_integration_in_db(job_id, job_id, exception, run_status, datetime.utcnow(), row_count=row_count)


def update_integration_in_db(celery_task_id, integration, error_message, run_status, start_date, row_count=0):
    db = database_utils.DatabaseUtils(**database_utils.get_open_etl_document_connection_details())
    db.update_integration(record_id=integration, is_running=False)
    db.update_integration_runtime(job_id=celery_task_id, error_message=error_message, run_status=run_status,
                                  end_date=start_date, row_count=row_count)


def run_pipeline_target(df, integration_id, spark_class, job_id, job_name, con_string, target_table, driver, spark_session, db_class,
                        logger, batch_size=100000):

    logger.info("Initializing writing to target")
    logger.info(df.limit(2))
    logger.info(df.dtypes)
    logger.exception(df.show())

    logger.info("Removing '.' from columns")
    df = df.selectExpr(*[f"`{col}` as `{col.replace('.', '_')}`" for col in df.columns])

    logger.info("Splitting into batches")
    total_rows = df.count()
    num_batches = (total_rows // batch_size) + (1 if total_rows % batch_size != 0 else 0)
    logger.info(f"Total rows: {total_rows}")
    logger.info(f"Number of batches: {num_batches}")

    # Adding row_number column for batch pagination
    window_spec = Window.orderBy(F.lit(1))  # A simple ordering, could be changed for better performance
    df_with_row_num = df.withColumn("row_number", F.row_number().over(window_spec))

    for i in range(num_batches):
        start = i * batch_size + 1  # start at 1 for row_number
        end = min((i + 1) * batch_size, total_rows)

        # Extract the batch by filtering on row_number
        batch_df = df_with_row_num.filter((F.col("row_number") >= start) & (F.col("row_number") <= end)).drop("row_number")
        batch_id = str(uuid.uuid4())
        logger.info(f"Batch ID: {batch_id}")
        db_class.insert_openetl_batch(batch_id=batch_id, integration_id=job_id, start_date=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), batch_type="full", batch_status="in progress", integration_name=job_name)

        logger.info(f"Processing batch {i + 1}/{num_batches}")

        if spark_class.write_via_spark(
                batch_df, conn_string=con_string, table=target_table, driver=driver):
            logger.info(f"Batch {i + 1}/{num_batches} processed successfully.")
            logger.info(f"Updating batch status for batch {i + 1}/{num_batches}")
            batch_df_size = batch_df.count()
            db_class.update_openetl_batch(batch_id=batch_id, integration_id=integration_id, batch_status="completed", end_date=datetime.now(
            ).strftime("%Y-%m-%d %H:%M:%S"), rows_count=batch_df_size)


