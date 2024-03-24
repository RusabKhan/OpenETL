import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

base_dir = os.getenv('OPENETL_HOME')
sys.path.append(base_dir)

from utils.airflow_utils import read_connection_table
import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

os.environ['NO_PROXY'] = '*'


default_args = {default_args}

source_connection = {source_connection}
target_connection = {target_connection}



logging.info("OPENETL_HOME: @VALUE".replace("@VALUE", base_dir))
logging.info("sys.path: @VALUE".replace("@VALUE", str(sys.path)))
logging.info("default_args: @VALUE".replace("@VALUE", str(default_args)))
logging.info("source_connection: @VALUE".replace("@VALUE", str(source_connection)))
logging.info("target_connection: @VALUE".replace("@VALUE", str(target_connection)))

# Define the DAG
dag = DAG(
    f"{integration_name}",
    default_args=default_args,
    description='A DAG to execute the get_data function',
    schedule_interval='@daily',
)


# Define the PythonOperator to execute the get_data function
execute_get_data = PythonOperator(
    task_id='execute_get_data',
    python_callable=read_from_source,
    op_args=source_connection,
    dag=dag,
)

# Set task dependencies
execute_get_data





