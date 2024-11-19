import sys
import os
from fastapi import APIRouter, Body, FastAPI, HTTPException, Request

from backend.models.airflow_model import CreatePipelineModel
from utils import airflow_utils

sys.path.append(os.environ['OPENETL_HOME'])
from utils.database_utils import DatabaseUtils

router = APIRouter(prefix="/airflow", tags=["airflow","scheduler","webserver"])


@router.post("/create_airflow_dag")
async def create_airflow_dag_api(request: Request, parameters: CreatePipelineModel = Body(...)):
    return airflow_utils.create_airflow_dag(**parameters.dict())
