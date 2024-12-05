import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

base_dir = os.getenv('OPENETL_HOME')
sys.path.append(base_dir)

from utils.pipeline_utils import run_pipeline
from utils.enums import *
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

os.environ['NO_PROXY'] = '*'


default_args = {default_args}

dag_name =  f"{integration_name}"
source_connection = {source_connection}
target_connection = {target_connection}
spark_config = {spark_config}
hadoop_config = {hadoop_config}


def print_environment_variables():
    logging.info("PRINTING OUT ENVIRONMENT VARIABLES")
    logging.info("OPENETL_HOME: @VALUE".replace("@VALUE", base_dir))
    logging.info("sys.path: @VALUE".replace("@VALUE", str(sys.path)))
    logging.info("default_args: @VALUE".replace("@VALUE", str(default_args)))
    logging.info("source_connection: @VALUE".replace("@VALUE", str(source_connection)))
    logging.info("target_connection: @VALUE".replace("@VALUE", str(target_connection)))
    logging.info("other env variables:")
    logging.info(os.environ)


# Define the DAG
dag = DAG(
    dag_name,
    default_args=default_args,
    description='A DAG to execute the get_data function',
    schedule_interval='@daily',
)

execute_print_environment_variables = PythonOperator(
    task_id='print_environment_variables',
    python_callable=print_environment_variables,
    dag=dag,
)

# Define the PythonOperator to execute the get_data function
execute_pipeline = PythonOperator(
    task_id='execute_pipeline',
    python_callable=run_pipeline,
    op_args=[source_connection['connection_type'], source_connection['table'], source_connection['schema'], \
    source_connection['connection_name'], target_connection['connection_type'], target_connection,
                spark_config, hadoop_config, dag_name],
    dag=dag,
)



# Set task dependencies
execute_print_environment_variables >> execute_pipeline





