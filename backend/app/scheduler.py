import json

from apscheduler.jobstores.base import JobLookupError
from fastapi import APIRouter, HTTPException, Body, Request
from openetl_utils.scheduler_utils import scheduler
import os
import redis


router = APIRouter(prefix="/scheduler", tags=["scheduler"])


REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379")
redis_client = redis.from_url(REDIS_URL)
REDIS_QUEUE_KEY = os.getenv('REDIS_QUEUE_KEY', 'openetl:trigger_queue')
REDIS_KILL_KEY = os.getenv("REDIS_KILL_KEY", "openetl:kill_queue")

@router.delete("/remove-job/{job_id}")
def remove_job(job_id: str):
    """
    Remove a job from the APScheduler.
    """
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Job {job_id} removed successfully."}
    except JobLookupError:
        raise HTTPException(status_code=404, detail="Job not found")

@router.get("/list-jobs")
def list_jobs():
    """
    List all scheduled jobs.
    """
    jobs = scheduler.get_jobs()
    job_list = [{"id": job.id, "name": job.name, "next_run_time": job.next_run_time} for job in jobs]
    return {"jobs": job_list}


@router.patch("/pause-job/{job_id}")
def pause_job(job_id: str):
    """
    Pause a job in the APScheduler.
    """
    try:
        scheduler.pause_job(job_id)
        return {"message": f"Job {job_id} paused successfully."}
    except JobLookupError:
        raise HTTPException(status_code=404, detail="Job not found")

@router.patch("/resume-job/{job_id}")
def resume_job(job_id: str):
    """
    Resume a paused job in the APScheduler.
    """
    try:
        scheduler.resume_job(job_id)
        return {"message": f"Job {job_id} resumed successfully."}
    except JobLookupError:
        raise HTTPException(status_code=404, detail="Job not found")

@router.get("/timezone")
async def get_scheduler_timezone():
    return str(scheduler.timezone)


@router.post("/trigger-job")
async def trigger_job(request: Request, fields: dict = Body(...)):
    """
    Manually trigger a job by adding it to the Redis trigger queue.
    """
    try:
        job_id = {"integration_id":fields["integration_id"]}
        redis_client.lpush(REDIS_QUEUE_KEY, json.dumps(job_id))
        return {"message": f"Job {job_id} added to trigger queue {REDIS_QUEUE_KEY}", "payload": job_id}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Failed to add job to queue: {e}")

@router.post("/kill-job")
async def kill_job(fields: dict = Body(...)):
    """
    Push a kill request (task_id + optional container_name) into the Redis kill queue.
    """
    try:
        kill_data = {"integration_id":fields["integration_id"]}
        redis_client.lpush(REDIS_KILL_KEY, json.dumps(kill_data))
        return {
            "payload": kill_data
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Failed to add kill request to queue: {e}")
