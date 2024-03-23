import utils.api_utils as api
import utils.sqlalchemy_engine_utils as sqla
from utils.enums import *
#import utils.spark_utils as su
from datetime import datetime
import json
import os
import utils.local_connection_utils as loc


def create_airflow_dag(config):
    """Store pipeline configuration in .local/pipelines directory

    Args:
        config (string): Name of the pipeline

    Returns:
        tuple: Boolean, Config. True if stored
    """
    
    integration_name = config['integration_name']
    source = config['source_connection_name']
    con_details = loc.read_single_config(source)
    auth = con_details['data']['auth']
    api = con_details['data']['api']
    op_args = [
        config['target_table'],
        config['source_table'],
        config['target_schema'],
        config['source_schema'],
        config['mapping']
    ]
    
    template = os.readfile(f"airflow_templates/{config}.py").decode("utf-8")
    template = template.format(integration_name=integration_name,source=source,op_args=op_args)
    # with open(f"airflow_dags/{config}.py", "w") as f:
    #     f.write(template)
    return True


def read_from_source(source_type,config):
    if source_type.lower() == ConnectionType.DATABASE.value:
        spark = su.SparkConnection(config)
        df = spark.read_via_spark()
        return df
    elif source_type.lower() == ConnectionType.API.value:
        return api.get_data(**config)