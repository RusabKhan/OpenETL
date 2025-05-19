import sys
import time
import os
import logging
from datetime import datetime

from celery import Celery
from celery.signals import after_setup_logger, task_prerun
from openetl_utils.database_utils import get_open_etl_document_connection_details, DatabaseUtils
import openetl_utils.pipeline_utils as pipeline
from openetl_utils.logger import get_logger

# Environment setup
LOG_DIR = f"{os.environ['OPENETL_HOME']}/.logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Global logging configuration
GLOBAL_LOG_FILE = f"{LOG_DIR}/celery.log"

logger = get_logger(name="celery", log_file=GLOBAL_LOG_FILE)

url = get_open_etl_document_connection_details(url=True)

app = Celery('openetl',
             broker=os.getenv("CELERY_BROKER_URL", f"redis://localhost:6379/0"),
             broker_connection_retry_on_startup=True,
             backend=f"db+{url}")  # Correct backend URL for task results

# Celery configuration
app.conf.task_routes = {'*.tasks.*': {'queue': 'default'}}
app.conf.result_backend = f"db+{url}"  # Ensure this is a valid result backend URL
app.conf.update(
    timezone='UTC',
    task_track_started=True,  # Track task start time
    enable_utc=True,
)


# Dynamically set log file for each job using `task_prerun`
@task_prerun.connect
def configure_task_logger(task_id=None, task=None, args=None, **kwargs):
    """
    Dynamically configure logging for each task based on job_id.
    This appends Celery worker logs to the job-specific log file and includes console logs.
    """
    if task.name == "openetl_utils.celery_utils.run_pipeline":
        # Extract job_id and job_name from args
        job_id = args[0] if args else "unknown_job"
        job_name = args[1] if len(args) > 1 else "unknown_name"

        # Log file for this job
        job_log_file = f"{LOG_DIR}/{job_id}-{job_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

        # Configure Celery worker logging for this task
        task_logger = logging.getLogger('celery')

        # File handler for job-specific log file
        file_handler = logging.FileHandler(job_log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # Stream handler to capture console logs
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)  # Set stream handler level to DEBUG
        stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # Add both handlers to the task logger
        task_logger.addHandler(file_handler)
        task_logger.addHandler(stream_handler)

        # Create a job-specific logger
        job_logger = logging.getLogger(f"job_{job_id}")
        job_logger.setLevel(logging.INFO)

        # Add the file handler and stream handler to the job-specific logger
        job_logger.addHandler(file_handler)
        job_logger.addHandler(stream_handler)

        # Set root logger level to NOTSET
        logging.getLogger('').setLevel(logging.NOTSET)

        # Log job configuration details
        job_logger.info(f"Configured logger for job_id: {job_id}, log file: {job_log_file}")
        job_logger.info(f"Task name: {task.name}")
        job_logger.info(f"Task arguments: {args}")



# Task definition
@app.task(bind=True)
def run_pipeline(self, job_id, job_name, job_type, source_connection, target_connection, source_table, target_table,
                 source_schema, target_schema, spark_config, hadoop_config, batch_size, **kwargs):
    # Log task start
    job_logger = logging.getLogger(f"job_{job_id}")
    job_logger.info(f"Starting pipeline: {job_name} (Job ID: {job_id})")

    try:
        # Actual task logic
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
            hadoop_config=hadoop_config,
            batch_size=batch_size,
            logger=job_logger
        )
        job_logger.info(f"Pipeline {job_name} completed successfully.")
    except Exception as e:
        job_logger.error(f"Pipeline {job_name} failed with error: {e}", exc_info=True)
        raise
    finally:
        # Clean up handlers to avoid duplication
        job_logger.handlers.clear()

# Utility function to get task details
def get_task_details(task_id):
    logger.info(f"Fetching task details for Task ID: {task_id}")
    return app.AsyncResult(task_id)


# Retry decorator
def retry(tries, delay):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < tries - 1:
                        time.sleep(delay)
                    else:
                        logger.error(f"All {tries} attempts failed for {func.__name__}.", exc_info=True)
                        raise
        return wrapper
    return decorator
