import sys
import os
from http.client import HTTPException
from urllib.error import HTTPError

from fastapi import APIRouter, Body, Request

from app.models.main import CreatePipelineModel
from starlette.responses import JSONResponse

from openetl_utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details, generate_cron_expression
from openetl_utils.enums import IntegrationType, LogsType
from openetl_utils.local_connection_utils import  paginate_log_content, get_log_file_path

sys.path.append(os.environ['OPENETL_HOME'])

router = APIRouter(prefix="/pipeline", tags=["pipeline", "scheduler", "webserver"])


@router.post("/create_integration")
async def create_pipeline_api(request: Request, pipeline_config: CreatePipelineModel = Body(...)):
    """
    Creates a new pipeline integration in the database.

    This endpoint receives a pipeline configuration, processes it to generate
    the necessary cron expression, and then stores the integration details in
    the database.

    Args:
        request (Request): The request object.
        pipeline_config (CreatePipelineModel): The configuration for the pipeline,
            including details like spark and hadoop configurations, integration name,
            connection details, and scheduling information.

    Returns:
        dict: The created pipeline integration details.

    Raises:
        HTTPException: If there is an error creating the integration.
    """
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


@router.post("/update_integration")
async def update_pipeline_api(request: Request, fields: dict = Body(...), pipeline_id: str = Body(...)):
    """
    Updates a pipeline in the database.

    Args:
        request (Request): The request object.
        fields (dict): A dictionary of fields to update.
        pipeline_id (str): The ID of the pipeline to update.

    Returns:
        dict: The updated pipeline configuration.

    Raises:
        HTTPException: If the pipeline ID is invalid.

    Notes:
        The `fields` dictionary should contain the fields to update, with the
        values being the new values for those fields.

        The `pipeline_id` parameter should be the ID of the pipeline to update.

        If the `schedule_date`, `schedule_time`, or `frequency` fields are
        present in `fields`, the `cron_expression` field will be generated
        automatically and the original fields will be deleted from `fields`.

        If the `integration_type` field is present in `fields`, it will be
        converted to an `IntegrationType` enum value.
    """
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    if "schedule_date" in fields or "schedule_time" in fields or "frequency" in fields:
        fields["cron_expression"] = generate_cron_expression(schedule_time=fields["schedule_time"],
                                                                      schedule_dates=fields["schedule_date"],
                                                                      frequency=fields["frequency"])
        del fields["frequency"]
        del fields["schedule_time"]
        del fields["schedule_date"]

    if "integration_type" in fields:
        fields["integration_type"] = IntegrationType(fields["integration_type"])

    return db.update_integration(record_id=pipeline_id, **fields)


@router.delete("/delete_integration")
async def delete_pipeline_api(request: Request, pipeline_id: str):
    """
    Deletes a pipeline from the database.

    Args:
        request (Request): The request object.
        pipeline_id (str): The ID of the pipeline to delete.

    Returns:
        bool: True if the pipeline was deleted successfully.

    Raises:
        HTTPException: If the pipeline ID is invalid.
    """
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    return db.delete_integration(record_id=pipeline_id)


@router.get("/get_integrations")
async def get_integrations_api(
        request: Request,
        integration_id: str | None = None,
        page: int = 1,
        page_size: int = 10,

):
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    if integration_id:
        return db.get_all_integration(integration_id=integration_id, page=page, per_page=page_size)
    return db.get_all_integration(page=page, per_page=page_size)

@router.get("/get_integration_history/{integration_id}")
async def get_integration_history_api(
        request: Request,
        integration_id: str | None = None,
        page: int = 1,
        page_size: int = 10,
):
    db = DatabaseUtils(**get_open_etl_document_connection_details())
    return db.get_integration_history(integration_id=integration_id, page=page, per_page=page_size)


@router.get("/get_logs/")
async def get_logs_api(
        request: Request,
        integration_id: str | None = None,
        logs_type: LogsType = LogsType.INTEGRATION,
        page: int = 1,
        per_page: int = 1000
):
    """
    Endpoint to get paginated log content.
    - Supports filtering by integration_id and logs_type.
    - Pagination via `page` and `per_page` query params.
    """
    logs_dir = os.path.join(os.environ['OPENETL_HOME'], ".logs")
    log_file_paths = get_log_file_path(logs_dir, integration_id, logs_type)

    log_content, total_pages = paginate_log_content(log_file_paths, page, per_page)

    return JSONResponse(content={
        "logs": log_content,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    })

