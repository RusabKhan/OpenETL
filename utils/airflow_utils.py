import pandas as pd
from utils.cache import *
import utils.local_connection_utils as loc
import json
from datetime import datetime, timedelta
import utils.spark_utils as su
from utils.enums import *
import utils.sqlalchemy_engine_utils as sqla
import utils.jdbc_engine_utils as jdbc_utils
import utils.api_utils as api
import sys
import os
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
        integration_name=integration_name, source_connection=op_args[
            "config"]["source"], target_connection=op_args["config"]["target"], mapping=config["mapping"],
        spark_config=config["spark_config"], hadoop_config=config["hadoop_config"], default_args=default_args)
    with open(f"{os.getcwd()}/.local/dags/{config['integration_name']}.py", "w") as f:
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
        spark = su.SparkConnection(config)
        df = spark.read_via_spark()
        return df
    elif connection_type.lower() == ConnectionType.API.value:
        data = api.read_connection_table(
            table=table, connection_name=connection_name)
        print("################################")
        print(data)
        return data


def extract_xcom_value(task_id, **context):
    # Extract XCom value
    xcom_value = context['task_instance'].xcom_pull(task_ids=task_id)

    # Do something with the XCom value
    print("Extracted XCom value:", xcom_value)
    return xcom_value


def run_pipeline(source_connection_type, source_table, source_schema, source_connection_name, target_connection_type,
                 target_connection_config, spark_config=None, hadoop_config=None,  mapping=None):

    logging.info("RUNNING PIPELINE")
    df = read_data(source_connection_type, source_table,
                   source_schema, source_connection_name)
    
    if target_connection_type.lower() == ConnectionType.DATABASE.value:
        connection_details = loc.read_single_connection_config(
            target_connection_config['connection_name'])
        engine = connection_details['engine']

        jar = jdbc_database_jars[engine]
        driver = jdbc_engine_drivers[engine]

        connection_details = {key.upper(): value for key,
                              value in connection_details.items()}
        con_string = jdbc_connection_strings[engine].format(
            **connection_details)
        spark_class = su.SparkConnection(spark_configuration=spark_config,
                                         hadoop_configuration=hadoop_config, jar=jar, connection_string=con_string)
        spark_session = spark_class.initializeSpark()
        df = spark_session.createDataFrame(df)
        spark_class.write_via_spark(
            df, conn_string=con_string, table=target_connection_config['table'], driver=driver, mode="overwrite")
    elif target_connection_type.lower() == ConnectionType.API.value:
        raise NotImplementedError("API target connection not implemented")
