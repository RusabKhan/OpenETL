import os
import sys
import uuid

sys.path.append(os.environ['OPENETL_HOME'])

import logging
import time
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from utils.celery_utils import app, run_pipeline, retry
from utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details
from utils.enums import RunStatus

# Global database and engine initialization


# Wrapper function for task execution
def send_task_to_celery(job_id, job_name, job_type, source_connection, target_connection, source_table, target_table, source_schema,
                          target_schema, spark_config, hadoop_config, batch_size, **kwargs):
    """
    Wrapper function to send tasks to Celery dynamically using apply_async.
    """
    logger.info(f"Sending task to Celery for job_id: {job_id}, job_name: {job_name}")
    try:
        app.send_task(name="utils.celery_utils.run_pipeline",
                      task_id=job_id,
                      args=[job_id, job_name, job_type, source_connection, target_connection, source_table, target_table,
                            source_schema, target_schema, spark_config, hadoop_config, batch_size],
                      kwargs=kwargs)
        logger.info(f"Task {job_id} sent successfully to Celery.")
    except Exception as e:
        logger.error(f"Error sending task {job_id} to Celery: {e}", exc_info=True)
        raise

    @retry(tries=3, delay=2)
    def update_db():
        try:
            db.update_integration(record_id=job_id, last_run=datetime.utcnow(), is_running=True)
            db.create_integration_history(
                celery_task_id=job_id,
                integration=job_id,
                error_message="",
                run_status=RunStatus.RUNNING,
                start_date=datetime.utcnow(),
            )
            logger.info(f"Integration {job_id} status updated to RUNNING in database.")
        except Exception as e:
            logger.error(f"Error updating database for job {job_id}: {e}", exc_info=True)

    update_db()

def check_and_schedule_tasks():
    """
    Check database for integrations and schedule tasks if needed.
    """
    logger.info("Checking and scheduling tasks.")
    integrations = db.get_integrations_to_schedule()
    current_jobs = scheduler.get_jobs()
    current_job_ids = {job.id for job in current_jobs}
    current_job_ids.remove(scheduler_job_id)  # Avoid removing the scheduler job itself
    integration_ids = {integration.id.__str__() for integration in integrations}
    disabled_integrations = {integration.id.__str__() for integration in integrations if not integration.is_enabled}

    # Remove jobs no longer in the database
    for job_id in current_job_ids - integration_ids:
        try:
            # Check if the job_id is a valid UUID
            uuid.UUID(job_id)  # This will raise an exception if it's not a valid UUID
            scheduler.remove_job(job_id)
            app.control.revoke(job_id, terminate=True)
            logger.info(f"Removed job: {job_id}. Not found in DB")
        except ValueError:
            # If job_id is not a valid UUID, do not remove it
            logger.info(f"Skipped removing job: {job_id}. Not a valid UUID.")

    # Remove disabled integrations
    for job_id in disabled_integrations:
        if job_id in current_job_ids:
            scheduler.remove_job(job_id)
            app.control.revoke(job_id, terminate=True)
            logger.info(f"Removed job: {job_id}. Disabled")

    # Schedule new integrations
    for integration in integrations:
        job_id = integration.id.__str__()
        job_name = integration.integration_name.__str__()
        job_type = integration.integration_type.__str__()
        cron_time = integration.cron_expression
        source_connection = integration.source_connection
        target_connection = integration.target_connection
        source_table = integration.source_table.__str__()
        target_table = integration.target_table.__str__()
        source_schema = integration.source_schema.__str__()
        target_schema = integration.target_schema.__str__()
        spark_config = integration.spark_config
        hadoop_config = integration.hadoop_config
        batch_size = integration.batch_size

        source_detials = db.get_created_connections(id=source_connection)[0]
        target_detials = db.get_created_connections(id=target_connection)[0]
        source_detials['auth_type'] = source_detials['auth_type'].value
        target_detials['auth_type'] = target_detials['auth_type'].value

        try:
            for cron in cron_time:
                scheduler.add_job(
                    func=send_task_to_celery,
                    trigger=CronTrigger.from_crontab(cron),
                    args=[job_id, job_name, job_type, source_detials, target_detials, source_table, target_table, source_schema, target_schema ,spark_config, hadoop_config, batch_size],
                    kwargs={},
                    id=job_id,
                    replace_existing=True,
                )
                logger.info(f"Integration {job_id} scheduled successfully with cron: {cron}")

        except Exception as e:
            logger.error(f"Error scheduling integration {job_id}: {e}", exc_info=True)
            pass


def clean_up_old_logs():
    """
    Clean up log files older than LOG_TTL days in the log directory.
    """
    LOG_TTL = int(os.getenv("LOG_TTL", 7))  # Default to 7 days if not set
    LOG_DIR = f"{os.environ['OPENETL_HOME']}/.logs"  # Replace with your actual log directory path
    current_time = time.time()
    threshold_time = current_time - (LOG_TTL * 86400)  # 86400 seconds = 1 day

    try:
        # Loop through files in the log directory
        for filename in os.listdir(LOG_DIR):
            file_path = os.path.join(LOG_DIR, filename)

            if os.path.isfile(file_path):
                # Get the last modified time of the file
                file_mtime = os.path.getmtime(file_path)

                # If the file is older than the threshold, delete it
                if file_mtime < threshold_time:
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {filename}")
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}", exc_info=True)




def start_scheduler():
    """
    Start the APScheduler with PostgreSQL jobstore and periodic tasks.
    """
    scheduler.remove_all_jobs()

    # Add a periodic job to check and schedule tasks every 30 seconds
    scheduler.add_job(
        func=check_and_schedule_tasks,
        trigger=IntervalTrigger(seconds=30),
        id=scheduler_job_id,
        replace_existing=True,
    )

    scheduler.add_job(
        func=clean_up_old_logs,
        trigger=IntervalTrigger(days=1),
        id="clean_up_old_logs",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with PostgreSQL jobstore.")

    # Gracefully handle shutdown
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down gracefully.")





if __name__ == '__main__':
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    engine = db.engine.url  # Using engine URL for jobstore
    scheduler_job_id = f"check_and_schedule_openetl_"
    global scheduler
    scheduler = BackgroundScheduler(jobstores={'default': SQLAlchemyJobStore(engine=db.engine)})

    # Configure logging
    LOG_DIR = f"{os.environ['OPENETL_HOME']}/.logs"  # Ensure this is set to the correct log directory
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, 'scheduler.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),  # Log to a file
            logging.StreamHandler()  # Optionally, also log to console
        ]
    )

    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # Console handler for logging to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    start_scheduler()
