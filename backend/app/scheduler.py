import sys
import os
from http.client import HTTPException
from celery.result import AsyncResult
from fastapi import APIRouter, Body, Request
from utils.celery_app import app as celery_app

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Fetch the status of a Celery task.
    """
    task = AsyncResult(task_id, app=celery_app)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Retrieve task status and result
    status = task.status
    result = task.result
    traceback = task.traceback

    return {
        "task_id": task_id,
        "status": status,
        "result": result,
        "traceback": traceback
    }