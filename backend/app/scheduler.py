from apscheduler.jobstores.base import JobLookupError
from fastapi import APIRouter, HTTPException
from openetl_utils.scheduler_utils import scheduler

router = APIRouter(prefix="/scheduler", tags=["scheduler"])




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