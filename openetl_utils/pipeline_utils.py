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
import re
import sys
# base_dir = os.getenv('OPENETL_HOME')
# sys.path.append(base_dir)
import uuid

import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import *

from sqlalchemy import MetaData, inspect
from sqlalchemy import Table, MetaData, Column, Integer, Float, String, Boolean, DateTime, BigInteger

import openetl_utils.connector_utils as con_utils
from openetl_utils.enums import RunStatus, ConnectionType, ColumnActions
from openetl_utils.__migrations__.batch import OpenETLBatch
from datetime import datetime
import openetl_utils.spark_utils as sp_ut
import openetl_utils.database_utils as database_utils
import logging

from openetl_utils.cache import jdbc_connection_strings, jdbc_engine_drivers, jdbc_database_jars

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def read_data(connector_name, auth_values, auth_type, table, connection_type, schema="public", config={},
              batch_size=None, logger=None):
    main_df = pd.DataFrame()

    if connection_type.lower() not in [ConnectionType.DATABASE.value, ConnectionType.API.value]:
        raise ValueError(f"Unsupported connection type: {connection_type}")

    if connection_type.lower() == ConnectionType.API.value:
        gen = con_utils.fetch_data_from_connector(connector_name, auth_values, auth_type, table, connection_type, schema=schema)
        for i, data in enumerate(gen):

            logger.info("RUNNING PAGE NUMBER {}".format(i + 1))
            logger.info("LOGGING DATA")
            logger.info(data)

            if not isinstance(data, pd.DataFrame):
                logger.error("Fetched data must be a pandas DataFrame")

            logger.info("LOGGING DATA")
            logger.info(data)

            if not isinstance(data, pd.DataFrame):
                raise ValueError("Fetched data must be a pandas DataFrame")

            main_df = pd.concat([main_df, data], ignore_index=True)

            while len(main_df) >= batch_size:
                yield main_df.iloc[:batch_size].copy()
                main_df = main_df.iloc[batch_size:].reset_index(drop=True)

    if batch_size and not main_df.empty:
        logger.info(f"Yielding leftover {len(main_df)} rows")
        yield main_df




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
    global row_count, db, batch_id, spark_class
    spark_class = None
    db = None
    batch_id = None
    exception = None
    run_status = None
    row_count = 0
    run_id = uuid.uuid4()
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

            db = database_utils.DatabaseUtils()
            db.engine, db.session = con_utils.create_db_connector_engine(target_connection_details['connector_name'], **target_credentials)

            db.create_table_from_base(base=OpenETLBatch)

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
                        batch_id = create_batch(db, job_id, job_name, logger)

                        row_count = df.count()
                        run_status = RunStatus.SUCCESS if run_pipeline_target(df=df, integration_id=job_id,
                                                                              spark_class=spark_class,
                                                                              con_string=con_string,
                                                                              target_table=target_table, job_id=job_id,
                                                                              job_name=job_name, driver=driver,
                                                                              spark_session=spark_session, db_class=db,
                                                                              logger=logger) else RunStatus.FAILED
            else:
                gen = read_data(connector_name=source_connection_details['connector_name'],
                                    auth_values=source_credentials,
                                    auth_type=source_connection_details['auth_type'],
                                    table=source_table,
                                    connection_type=source_connection_details['connection_type'],
                                    schema=source_schema,
                                    batch_size=batch_size,
                                    logger=logger)
                for df in gen:
                    row_count = 0

                    if not df.empty:
                        batch_id = create_batch(db, job_id, job_name, logger, run_id)


                        logger.info(df)

                        df = coerce_inferable_columns(df, spark_session, logger)
                        logger.info("DF AFTER INFERABLE CONVERSION")
                        logger.info(df)
                        logger.info(df.dtypes)

                        logger.info("Replacing null values")
                        df = df.fillna(np.nan)  # optional, Pandas already treats NaNs as NaNs
                        fill_map = {
                            'int': 0,
                            'float': 0.0,
                            'bool': False,
                            'string': '',
                            'object': '',
                            'datetime': pd.Timestamp('1970-01-01'),
                            'timedelta': pd.Timedelta(0),
                            'category': '',
                            'bytes': b'',
                            'complex': 0j,
                        }

                        df = df.fillna({
                            col: next((v for k, v in fill_map.items() if k in str(df[col].dtype).lower()), '')
                            for col in df.columns
                        })

                        logger.info("DF AFTER REPLACING NULL VALUES")
                        logger.info(df)

                        df = spark_session.createDataFrame(df)
                        logger.info("DF AFTER CONVERSION TO SPARK DF")
                        logger.info(df)
                        logger.info(df.dtypes)
                        row_count = df.count()

                        logger.info("Replacing null values")


                        create_table_from_spark_df(df=df, engine=db.engine, table_name=target_table, schema_name=target_credentials['schema'])

                        run_status = RunStatus.SUCCESS if run_pipeline_target(df=df, integration_id=job_id, spark_class=spark_class,
                                            con_string=con_string,
                                            target_table=target_table, job_id=job_id, job_name=job_name, driver=driver,
                                            spark_session=spark_session, db_class=db, logger=logger) else RunStatus.FAILED


        elif target_connection_details['connection_type'].lower() == ConnectionType.API.value:
            raise NotImplementedError("API target connection not implemented")

    except Exception as e:
        exception = str(e)
        logger.error(e)
        run_status = RunStatus.FAILED
        if batch_id:
            complete_batch(db, batch_id, job_id, row_count, logger, batch_status=run_status)
    finally:
        update_integration_in_db(job_id, job_id, exception, run_status, datetime.utcnow(), row_count=row_count)
        logger.info("FINISHED PIPELINE")
        logger.info("DISPOSING ENGINES")
        if spark_class:
            spark_class.__dispose__()
        if db:
            db.__dispose__()



def update_integration_in_db(celery_task_id, integration, error_message, run_status, start_date, row_count=0):
    db = database_utils.DatabaseUtils(**database_utils.get_open_etl_document_connection_details())
    db.update_integration(record_id=integration, is_running=False)
    db.update_integration_runtime(job_id=celery_task_id, error_message=error_message, run_status=run_status,
                                  end_date=start_date, row_count=row_count)


def create_batch(db_class, job_id, job_name, logger, run_id):
    batch_id = str(uuid.uuid4())
    logger.info(f"Creating batch ID: {batch_id}")
    db_class.insert_openetl_batch(
        batch_id=batch_id,
        integration_id=str(job_id),
        start_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        batch_type="full",
        batch_status=RunStatus.RUNNING,
        integration_name=job_name,
        run_id=str(run_id)
    )
    return batch_id

def complete_batch(db_class, batch_id, integration_id, batch_df_size, logger, batch_status=RunStatus.SUCCESS):
    logger.info(f"Completing batch ID: {batch_id}")
    db_class.update_openetl_batch(
        batch_id=batch_id,
        integration_id=integration_id,
        batch_status=batch_status,
        end_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rows_count=batch_df_size
    )


def run_pipeline_target(df, integration_id, spark_class, job_id, job_name, con_string, target_table, driver,
                        spark_session, db_class, logger):
    logger.info("Initializing writing to target")
    logger.info(df.limit(2))
    logger.info(df.dtypes)
    logger.debug(df.show(truncate=False))

    logger.info("Sanitizing column names")
    df = df.selectExpr(*[f"`{col}` as `{col.replace('.', '_')}`" for col in df.columns])

    logger.info(f"Writing full DataFrame to target table: {target_table}")
    success, message = spark_class.write_via_spark(df, conn_string=con_string, table=target_table, driver=driver)

    if success:
        logger.info("Data written successfully. Updating batch status.")
        complete_batch(db_class, batch_id, integration_id, row_count, logger)
    else:
        logger.error(message)
        raise Exception(message)

    return success

def coerce_inferable_columns(df: pd.DataFrame, spark_session: SparkSession, logger):
    """
    Attempt to create a Spark DataFrame from each column individually to detect schema inference issues.
    If inference fails for any column, it is cast to string to avoid Spark type merge errors.
    Args:
        df (pd.DataFrame): The input Pandas DataFrame.
        spark_session (SparkSession): Active Spark session for testing type inference.
        logger: Logger instance for warning messages.
    Returns:
        pd.DataFrame: Cleaned DataFrame with problematic columns coerced to string.
    """
    for col in df.columns:
        try:
            _ = spark_session.createDataFrame(df[[col]])
        except Exception as e:
            logger.warning(f"Unable to infer type for column {col}: {e}")
            df[col] = df[col].astype(str)
    return df


def map_spark_type_to_sqlalchemy(spark_type, max_len=None):
    from sqlalchemy import Integer, BigInteger, Float, Boolean, DateTime

    if isinstance(spark_type, IntegerType):
        return Integer
    elif isinstance(spark_type, LongType):
        return BigInteger
    elif isinstance(spark_type, (FloatType, DoubleType)):
        return Float
    elif isinstance(spark_type, StringType):
        return String(max_len + 50 if max_len else 255)
    elif isinstance(spark_type, BooleanType):
        return Boolean
    elif isinstance(spark_type, (TimestampType, DateType)):
        return DateTime
    else:
        return String(255)

def create_table_from_spark_df(df, engine, table_name, schema_name="public"):
    inspector = inspect(engine)
    if inspector.has_table(table_name, schema=schema_name):
        return  # Table exists, do nothing

    metadata = MetaData(schema=schema_name)
    columns = []

    for field in df.schema.fields:
        max_len = None
        if isinstance(field.dataType, StringType):
            max_len = df.selectExpr(f"length({field.name})").agg({"length({})".format(field.name): "max"}).collect()[0][0]
            max_len = max_len if max_len else 0

        col_type = map_spark_type_to_sqlalchemy(field.dataType, max_len)
        col = Column(field.name, col_type, nullable=field.nullable)
        columns.append(col)

    sql_table = Table(table_name, metadata, *columns)
    metadata.create_all(engine, tables=[sql_table])
