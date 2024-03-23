import os
import sys

base_dir = os.getenv('OPENETL_HOME')
sys.path.append(base_dir)

from utils.airflow_utils import read_from_source
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

default_args = {default_args}

# Define the DAG
dag = DAG(
    {integration_name},
    default_args=default_args,
    description='A DAG to execute the get_data function',
    schedule_interval='@daily',
)

op_args = {op_args}

# Define the PythonOperator to execute the get_data function
execute_get_data = PythonOperator(
    task_id='execute_get_data',
    python_callable=read_from_source,
    op_args=op_args,
    dag=dag,
)

# Set task dependencies
execute_get_data

# Set task dependencies
execute_get_data





