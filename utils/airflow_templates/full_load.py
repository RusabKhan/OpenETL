import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

base_dir = os.getenv('OPENETL_HOME')
sys.path.append(base_dir)

from utils.airflow_utils import read_data, extract_xcom_value
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

os.environ['NO_PROXY'] = '*'


default_args = {default_args}

source_connection = {source_connection}
target_connection = {target_connection}


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
    f"{integration_name}",
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
execute_get_data = PythonOperator(
    task_id='execute_get_data',
    python_callable=read_data,
    op_args=[source_connection['connection_type'], source_connection['table'], source_connection['schema'], source_connection['connection_name']],
    dag=dag,
)


task_to_extract_xcom = PythonOperator(
    task_id='task_to_extract_xcom',
    python_callable=extract_xcom_value,
    op_args=['execute_get_data'],
    dag=dag,
    provide_context=True,  # This is important to provide the context to the PythonOperator
)

# Set task dependencies
execute_print_environment_variables >> execute_get_data >> task_to_extract_xcom





