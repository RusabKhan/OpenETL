import time
from datetime import datetime, timedelta
from .celery_app import app
from .database_utils import DatabaseUtils, get_open_etl_document_connection_details

class Scheduler:
    def __init__(self, celery_app = app):
        self.celery_app = celery_app

    def heartbeat(self):
        while True:
            # Fetch all integrations from the table
            conn = DatabaseUtils(**get_open_etl_document_connection_details())
            integrations = conn.get_integrations_to_schedule()
            now = datetime.utcnow()

            for integration in integrations:
                next_run_time = integration.next_run_time

                # Check if the integration is due for scheduling
                if next_run_time and next_run_time <= now:
                    try:
                        # Schedule the task using Celery
                        celery_task = self.celery_app.send_task(
                            'integration_task',  # Replace with your Celery task name
                            args=[integration.uid],
                            kwargs={'data': integration.additional_data}  # Optional: Pass additional data
                        )

                        # Update next_run_time (example: schedule after 1 hour)
                        integration.next_run_time = now + timedelta(hours=1)
                        conn.update_integration(record_id = integration.uid, next_run_time=integration.next_run_time,
                                                is_running=True)
                        conn.create_integration_history(integration=integration.uid,
                                                        error_message=None,
                                                        last_run_status=None,
                                                        start_date=now,
                                                        end_date=None,
                                                        celery_task_id=celery_task.id
                                                        )

                        print(f"Integration {integration.uid} scheduled successfully.")
                    except Exception as e:
                        print(f"Failed to schedule integration {integration.uid}: {e}")

            # Wait for 30 seconds before the next check
            time.sleep(30)
