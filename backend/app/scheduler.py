import sys
import os
from http.client import HTTPException
from celery.result import AsyncResult
from fastapi import APIRouter, Body, Request
from utils.celery_utils import app as celery_app, get_task_details

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Fetch the status of a Celery task.
    """
    task = get_task_details(task_id)

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

