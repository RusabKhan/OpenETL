import os
import sys
import uuid

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


sys.path.append(os.environ['OPENETL_HOME'])

import logging
import time
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from openetl_utils.celery_utils import app, run_pipeline, retry
from openetl_utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details
from openetl_utils.enums import RunStatus
from openetl_utils.logger import get_logger

db = DatabaseUtils(**get_open_etl_document_connection_details())
engine = db.engine.url
scheduler_job_id = f"check_and_schedule_openetl_"

executors = {'default': ThreadPoolExecutor(max_workers=2), 'processpool': ProcessPoolExecutor(max_workers=2)}
job_defaults = {
    'max_instances': 1,
    'misfire_grace_time': 60 * 60,
    'coalesce': True,  # Prevent jobs being run being run in parallel if the server was down for a while.
}

# Configure logging
LOG_DIR = f"{os.environ['OPENETL_HOME']}/.logs"  # Ensure this is set to the correct log directory
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'scheduler.log')


logger = get_logger(name="scheduler", log_file=LOG_FILE, level=logging.INFO)

scheduler = BackgroundScheduler(jobstores={'default': SQLAlchemyJobStore(engine=db.engine)}, executors=executors,
                                job_defaults=job_defaults,
                                logger=logger,
                                timezone='UTC')

# Wrapper function for task execution
def send_task_to_celery(job_id, job_name, job_type, source_connection, target_connection, source_table, target_table,
                        source_schema,
                        target_schema, spark_config, hadoop_config, batch_size, **kwargs):
    """
    Wrapper function to send tasks to Celery dynamically using apply_async.
    """
    logger.info(f"Sending task to Celery for job_id: {job_id}, job_name: {job_name}")
    try:
        app.send_task(name="openetl_utils.celery_utils.run_pipeline",
                      task_id=job_id,
                      args=[job_id, job_name, job_type, source_connection, target_connection, source_table,
                            target_table,
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

    # Force a fresh query from the database
    integrations = db.get_integrations_to_schedule()

    # Ensure the session is fresh and not using cached data
    db.session.expire_all()  # Expire all objects in the session to avoid stale data

    current_jobs = scheduler.get_jobs()
    current_job_ids = {job.id for job in current_jobs if job.id != scheduler_job_id}  # Exclude scheduler job
    integration_ids = {integration.id.__str__() for integration in integrations}
    disabled_integrations = {integration.id.__str__() for integration in integrations if not integration.is_enabled}

    # Remove jobs not in database
    for job_id in current_job_ids - integration_ids:
        try:
            uuid.UUID(job_id)  # Ensure job_id is a valid UUID
            scheduler.remove_job(job_id)
            logger.info(f"Removed old job: {job_id}. Not found in DB.")
        except ValueError:
            logger.warning(f"Job ID {job_id} is not a valid UUID. Skipping removal.")

    # Remove jobs for disabled integrations
    for job_id in disabled_integrations:
        if job_id in current_job_ids:
            scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}. Disabled")

    # Schedule new integrations
    for integration in integrations:
        job_id = str(integration.id)  # Safely convert to string
        job_name = str(integration.integration_name)
        job_type = str(integration.integration_type)
        cron_time = integration.cron_expression
        source_connection = integration.source_connection
        target_connection = integration.target_connection
        source_table = str(integration.source_table)
        target_table = str(integration.target_table)
        source_schema = str(integration.source_schema)
        target_schema = str(integration.target_schema)
        spark_config = integration.spark_config
        hadoop_config = integration.hadoop_config
        batch_size = integration.batch_size

        source_details = db.get_created_connections(id=source_connection)[0]
        target_details = db.get_created_connections(id=target_connection)[0]
        source_details['auth_type'] = source_details['auth_type'].value
        target_details['auth_type'] = target_details['auth_type'].value

        try:
            for cron in cron_time:
                scheduler.add_job(
                    func=send_task_to_celery,
                    trigger=CronTrigger.from_crontab(cron),
                    args=[job_id, job_name, job_type, source_details, target_details, source_table, target_table,
                          source_schema, target_schema, spark_config, hadoop_config, batch_size],
                    kwargs={},
                    id=job_id,
                    replace_existing=True,
                )
                logger.info(f"Integration {job_id} scheduled successfully with cron: {cron}")

        except Exception as e:
            logger.error(f"Error scheduling integration {job_id}: {e}", exc_info=True)


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
        trigger=IntervalTrigger(seconds=15),
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
            jobs = scheduler.get_jobs()
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down gracefully.")


if __name__ == '__main__':
    start_scheduler()
