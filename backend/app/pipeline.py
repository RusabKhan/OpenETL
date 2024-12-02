import sys
import os
from http.client import HTTPException
from urllib.error import HTTPError

from fastapi import APIRouter, Body, Request

from backend.app.models.airflow_model import CreatePipelineModel
from utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details, generate_cron_expression
from utils.enums import IntegrationType

sys.path.append(os.environ['OPENETL_HOME'])

router = APIRouter(prefix="/pipeline", tags=["pipeline","scheduler","webserver"])


@router.post("/create_integration")
async def create_pipeline_api(request: Request, pipeline_config: CreatePipelineModel = Body(...)):
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    pipeline_config = pipeline_config.dict()
    pipeline_config["cron_expression"] = generate_cron_expression(schedule_time=pipeline_config["schedule_time"],
                                                                  schedule_dates=pipeline_config["schedule_date"],
                                                                  frequency=pipeline_config["frequency"])
    pipeline_config["integration_type"] = IntegrationType(pipeline_config["integration_type"])
    del pipeline_config["frequency"]
    del pipeline_config["schedule_time"]
    del pipeline_config["schedule_date"]

    return db.create_integration(**pipeline_config)
