import sys
import os
from datetime import timedelta
from http.client import HTTPException
from celery.result import AsyncResult
from fastapi import APIRouter, Body, Request
from utils.celery_utils import app as celery_app, get_task_details

router = APIRouter(prefix="/worker", tags=["worker","celery"])


# Fetch the status of a Celery task
@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Fetch the status of a Celery task.
    """
    task = get_task_details(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result,
        "traceback": task.traceback
    }


# Fetch the logs of a specific Celery task
@router.get("/task-logs/{task_id}")
async def get_task_logs(task_id: str):
    """
    Fetch the logs of a specific Celery task.
    """
    try:
        task = AsyncResult(task_id, app=celery_app)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Assuming logs are stored separately; replace with your log-fetching logic
        log_file = f"logs/{task_id}.log"
        if not os.path.exists(log_file):
            raise HTTPException(status_code=404, detail="Log file not found")

        with open(log_file, "r") as file:
            logs = file.read()

        return {"task_id": task_id, "logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fetch Celery worker status
@router.get("/worker-status")
async def get_worker_status():
    """
    Fetch the status of Celery workers.
    """
    try:
        inspect = celery_app.control.inspect()
        active_workers = inspect.active() or {}
        registered_tasks = inspect.registered() or {}

        return {
            "active_workers": list(active_workers.keys()),
            "registered_tasks": registered_tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching worker status: {str(e)}")


# Fetch task retry details
@router.get("/task-retries/{task_id}")
async def get_task_retries(task_id: str):
    """
    Fetch retry details of a Celery task.
    """
    task = AsyncResult(task_id, app=celery_app)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    retries = task.retries
    return {"task_id": task_id, "retries": retries}


# Revoke a Celery task
@router.post("/task-revoke/{task_id}")
async def revoke_task(task_id: str, terminate: bool = False):
    """
    Revoke a Celery task.
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        return {"message": f"Task {task_id} revoked", "terminated": terminate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error revoking task: {str(e)}")


@router.get("/tasks")
async def get_all_tasks():
    """
    Retrieve details of all active and scheduled tasks.
    """
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active() or {}
        scheduled = inspect.scheduled() or {}
        reserved = inspect.reserved() or {}

        return {
            "active_tasks": active,
            "scheduled_tasks": scheduled,
            "reserved_tasks": reserved,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


@router.get("/queue-info")
async def get_queue_info():
    """
    Get information about the task queues.
    """
    try:
        inspect = celery_app.control.inspect()
        queues = inspect.active_queues() or {}
        return {"queues": queues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching queue info: {str(e)}")


@router.delete("/clear-tasks")
async def clear_tasks():
    """
    Clear tasks from the backend based on status (e.g., SUCCESS, FAILURE).
    """
    try:
        backend = celery_app.backend
        if not hasattr(backend, "cleanup"):
            raise HTTPException(status_code=400, detail="Backend does not support cleanup.")

        # Call the backend's cleanup function with the specific task status
        backend.cleanup()
        return {"message": f"Cleared tasks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing tasks: {str(e)}")


@router.get("/task-history/{task_id}")
async def get_task_history(task_id: str):
    """
    Fetch the execution history of a task.
    """
    try:
        task = AsyncResult(task_id, app=celery_app)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        history = {
            "task_id": task_id,
            "status": task.status,
            "date_done": task.date_done,
            "traceback": task.traceback,
            "result": task.result,
        }

        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task history: {str(e)}")


#@router.post("/reschedule-task/")
async def reschedule_task(task_id: str = Body(...), eta: str = Body(...)):
    """
    Reschedule a task to run at a new time (ETA).
    """
    from datetime import datetime

    try:
        # Parse ETA (ensure it's in a valid datetime format)
        celery_app.control.revoke(task_id)

        # Re-apply the task with the new ETA
        task = AsyncResult(task_id, app=celery_app)
        if task.state not in ["SUCCESS", "FAILURE", "REVOKED"]:
            # Revoke if running or pending
            task.forget()
            task.revoke(terminate=True)

        # Apply the task with the new ETA
        if eta is None:
            eta = datetime.now() + timedelta(minutes=10)# Default ETA 10 minutes from now
        else:
            eta = datetime.fromisoformat(eta)

        return celery_app.send_task(
            id=task_id,
            name=task.name,
            args=task.args or [],
            kwargs=task.kwargs or {},
            eta=eta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rescheduling task: {str(e)}")


@router.get("/task-error/{task_id}")
async def get_task_error(task_id: str):
    """
    Fetch detailed error reports for a failed task.
    """
    task = AsyncResult(task_id, app=celery_app)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "FAILURE":
        return {"task_id": task_id, "message": "Task has not failed"}

    return {
        "task_id": task_id,
        "traceback": task.traceback,
        "result": task.result
    }
