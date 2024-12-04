import os
import sys

sys.path.append(os.environ['OPENETL_HOME'])

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from utils.celery_utils import app, run_pipeline, retry
from utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from utils.enums import RunStatus

# Global database and engine initialization
db = DatabaseUtils(**get_open_etl_document_connection_details())
engine = db.engine.url  # Using engine URL for jobstore

# Wrapper function for task execution
def send_task_to_celery(integration_uid, task_name='task_test', **kwargs):
    """
    Wrapper function to send tasks to Celery dynamically using apply_async.
    :param integration_uid: ID of the integration.
    :param task_name: Name of the Celery task (defaults to 'task').
    :param kwargs: Additional arguments for the Celery task.
    """
    # Apply the task asynchronously using apply_async
    celery_app_details = app.send_task("utils.celery_app.run_pipeline", args=[integration_uid], kwargs=kwargs)

    @retry(tries=3, delay=2)
    def update_db():
        db.update_integration(record_id=integration_uid, last_run=datetime.utcnow(), is_running=True)
        db.create_integration_history(
            celery_task_id=celery_app_details.id,
            integration=integration_uid,
            error_message="",
            run_status=RunStatus.RUNNING,
            start_date=datetime.utcnow(),
        )
    update_db()


def check_and_schedule_tasks():
    """
    Check database for integrations and schedule tasks if needed.
    """
    now = datetime.utcnow()
    integrations = db.get_integrations_to_schedule()

    for integration in integrations:
        cron_time = integration.cron_expression  # Assume this is a valid cron expression string.
        job_id = f"{integration.id}"

        try:
            # Add or update a job with CronTrigger to send the task to Celery dynamically
            scheduler.add_job(
                func=send_task_to_celery,  # Reference the send_task_to_celery function dynamically
                trigger=CronTrigger.from_crontab(cron_time),
                args=[integration.id],  # Pass the integration ID to the task
                kwargs={'task_name': 'task_test'},  # You can dynamically pass the task name if needed
                id=job_id,
                replace_existing=False,
            )
            print(f"Integration {job_id} scheduled successfully with cron: {cron_time}")
        except Exception as e:
            pass


def start_scheduler():
    """
    Start the APScheduler with PostgreSQL jobstore and periodic tasks.
    """
    global scheduler
    scheduler = BackgroundScheduler(jobstores={'default': SQLAlchemyJobStore(engine=db.engine)})
    scheduler.remove_all_jobs()

    # Add a periodic job to check and schedule tasks every 30 seconds
    scheduler.add_job(
        func=check_and_schedule_tasks,
        trigger=IntervalTrigger(seconds=10),
        id='check_and_schedule',
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
