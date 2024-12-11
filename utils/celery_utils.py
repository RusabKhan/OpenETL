import time
import os
from celery import Celery
from utils.database_utils import get_open_etl_document_connection_details, DatabaseUtils
import utils.pipeline_utils as pipeline

# Initialize Celery app with the broker
url = get_open_etl_document_connection_details(url=True)
app = Celery('openetl', broker=os.getenv("CELERY_BROKER_URL", f"redis://localhost:6379/0"))

# Route tasks to the default queue
app.conf.task_routes = {'*.tasks.*': {'queue': 'default'}}
app.conf.result_backend = f"db+{url}"

# Celery configuration settings (if needed, add more here)
app.conf.update(
    timezone='UTC',  # Set your preferred timezone
    enable_utc=True,  # Ensure UTC-based scheduling if timezone isn't specified
)

@app.task()
def run_pipeline(job_id, job_name,job_type, source_connection, target_connection, source_table, target_table, source_schema,
                          target_schema, spark_config, hadoop_config, **kwargs):
        pipeline.run_pipeline(
            job_type=job_type,
            job_id=job_id,
            job_name=job_name,
            source_connection_details=source_connection,
            target_connection_details=target_connection,
            source_schema=source_schema,
            target_schema=target_schema,
            source_table=source_table,
            target_table=target_table,
            spark_config=spark_config,
            hadoop_config=hadoop_config
        )




def get_task_details(task_id):
    return app.AsyncResult(task_id)

def retry(tries, delay):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < tries - 1:
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator

