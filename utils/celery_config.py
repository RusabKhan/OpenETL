from celery import Celery

# Initialize Celery app with the broker
app = Celery('openetl', broker='redis://redis:6379/0')

# Route tasks to the default queue
app.conf.task_routes = {'*.tasks.*': {'queue': 'default'}}

# Custom filename for the beat schedule (optional)
app.conf.beat_schedule_filename = '/app/celerybeat-schedule'  # Use an absolute path for reliability

# Celery configuration settings (if needed, add more here)
app.conf.update(
    timezone='UTC',  # Set your preferred timezone
    enable_utc=True,  # Ensure UTC-based scheduling if timezone isn't specified
)