import os
import sys

from click.core import batch

sys.path.append(os.environ['OPENETL_HOME'])

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from utils.celery_utils import app, run_pipeline, retry
from utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from utils.enums import RunStatus
import uuid

# Global database and engine initialization
db = DatabaseUtils(**get_open_etl_document_connection_details())
engine = db.engine.url  # Using engine URL for jobstore
scheduler_job_id = f"check_and_schedule_openetl_"
global scheduler
scheduler = BackgroundScheduler(jobstores={'default': SQLAlchemyJobStore(engine=db.engine)})


# Wrapper function for task execution
def send_task_to_celery(job_id, job_name, job_type, source_connection, target_connection, source_table, target_table, source_schema,
                          target_schema, spark_config, hadoop_config, batch_size, **kwargs):
    """
    Wrapper function to send tasks to Celery dynamically using apply_async.
    :param integration_uid: ID of the integration.
    :param task_name: Name of the Celery task (defaults to 'task').
    :param kwargs: Additional arguments for the Celery task.
    """
    # Apply the task asynchronously using apply_async

    app.send_task(name="utils.celery_utils.run_pipeline",
                                       task_id=job_id,
                                       args=[job_id, job_name,job_type, source_connection, target_connection, source_table, target_table, source_schema,
                          target_schema, spark_config, hadoop_config, batch_size], kwargs=kwargs)
    @retry(tries=3, delay=2)
    def update_db():
        db.update_integration(record_id=job_id, last_run=datetime.utcnow(), is_running=True)
        db.create_integration_history(
            celery_task_id=job_id,
            integration=job_id,
            error_message="",
            run_status=RunStatus.RUNNING,
            start_date=datetime.utcnow(),
        )
    update_db()




def check_and_schedule_tasks():
    """
    Check database for integrations and schedule tasks if needed.
    """
    integrations = db.get_integrations_to_schedule()
    current_jobs = scheduler.get_jobs()
    current_job_ids = {job.id for job in current_jobs}
    current_job_ids.remove(scheduler_job_id)
    integration_ids = {integration.id.__str__() for integration in integrations}
    disabled_integrations = {integration.id.__str__() for integration in integrations if not integration.is_enabled}

    for job_id in current_job_ids - integration_ids:
        scheduler.remove_job(job_id)
        app.control.revoke(job_id, terminate=True)
        print(f"Removed job: {job_id}. Not found in DB")
        integrations = [integration for integration in integrations if integration.id.__str__() != job_id]

    for job_id in disabled_integrations:
        integrations = [integration for integration in integrations if integration.id.__str__() != job_id]
        if job_id in current_job_ids:
            scheduler.remove_job(job_id)
            app.control.revoke(job_id, terminate=True)
            print(f"Removed job: {job_id}. Disabled")

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

        source_detials = db.get_created_connections(id=source_connection)[0]
        target_detials = db.get_created_connections(id=target_connection)[0]
        source_detials['auth_type'] = source_detials['auth_type'].value
        target_detials['auth_type'] = target_detials['auth_type'].value
        batch_size = integration.batch_size

        try:
            for cron in cron_time:
                scheduler.add_job(
                    func=send_task_to_celery,
                    trigger=CronTrigger.from_crontab(cron),
                    args=[job_id, job_name, job_type, source_detials, target_detials, source_table, target_table, source_schema, target_schema ,spark_config, hadoop_config,
                          batch_size],
                    kwargs={},
                    id=job_id,
                    replace_existing=True,
                )
                print(f"Integration {job_id} scheduled successfully with cron: {cron_time}")

        except Exception as e:
            print(f"Error scheduling integration {job_id}: {e}")
            pass


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
    scheduler.start()
    print("Scheduler started with PostgreSQL jobstore.")

    # Gracefully handle shutdown
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        print("Scheduler shut down gracefully.")

if __name__ == '__main__':
    start_scheduler()
