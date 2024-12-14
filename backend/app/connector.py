from fastapi import APIRouter, Body, HTTPException, Request
import os
import sys

from backend.app.models.main import ConnectionBody

sys.path.append(os.environ['OPENETL_HOME'])

from app.models.main import IntegrationBody
from utils.connector_utils import get_installed_connectors
from utils.enums import AuthType, ConnectionType

from utils.database_utils import DatabaseUtils, get_open_etl_document_connection_details
import utils.connector_utils as con_utils

router = APIRouter(prefix="/connector", tags=["connector"])


@router.get("/get_installed_connectors")
async def get_installed_connectors_api():
    database_sources = get_installed_connectors(ConnectionType.DATABASE)
    api_engines = get_installed_connectors(ConnectionType.API)
    return {"database": database_sources, "api": api_engines}


@router.post("/test_connection")
async def test_connection_api(request: Request, connector_name: str = Body(...), connector_type: str = Body(...),
                              auth_type: str = Body(...), auth_params: dict = Body(...)):
    return con_utils.connector_test_connection(connector_name, ConnectionType(connector_type), auth_type, **auth_params)


@router.post("/store_connection")
async def store_connection_api(request: Request, connection_credentials: dict = Body(...),
                               connection_name: str = Body(...), connection_type: str = Body(...),
                               connector_name: str = Body(...), auth_type: str = Body(...)):
    vals = get_open_etl_document_connection_details()
    auth_type = AuthType(auth_type)
    data = {"connection_credentials": connection_credentials, "connection_name": connection_name,
            "connection_type": connection_type, "auth_type": auth_type, "connector_name": connector_name}
    return DatabaseUtils(**vals).write_document(data)


@router.get("/get_connector_auth_details/{connector_name}/{connector_type}")
async def get_connector_auth_details_api(request: Request, connector_name: str, connector_type: str):
    connector_type = ConnectionType(connector_type)
    return con_utils.get_connector_auth_details(connector_name, connector_type)


@router.get("/get_connector_image/{connector_name}/{connector_type}")
async def get_connector_image_api(request: Request, connector_name: str, connector_type: str):
    return con_utils.get_connector_image(connector_name, connector_type)


@router.get("/get_connector_metadata/{connector_name}/{connector_type}")
async def get_connector_metadata_api(request: Request, connector_name: str, connector_type: str):
    connector_type = ConnectionType(connector_type)
    return con_utils.get_connector_metadata(connector_name, connector_type)


@router.post("/get_created_connections")
async def created_connections_api(request: Request, connector_type: str = Body(...), connection_name: str = Body(None)):
    try:
        return con_utils.get_created_connections(connector_type, connection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch_metadata")
async def connector_fetch_metadata_api(request: Request):
    try:
        body = await request.json()
        connector_name = body.get("connector_name")
        connector_type = body.get("connector_type")
        auth_options = body.get("auth_options")
        return con_utils.fetch_metadata(connection=connector_name, connection_type=connector_type,
                                        auth_options=auth_options)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_connection")
async def update_connection_api(request: Request, document_id: int = Body(...), fields: ConnectionBody = Body(...)):
    try:
        db = DatabaseUtils(**get_open_etl_document_connection_details())
        return db.update_openetl_document(document_id=document_id, **fields.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_connection")
async def delete_connection_api(request: Request, document_id: int):
    try:
        db = DatabaseUtils(**get_open_etl_document_connection_details())
        return db.delete_document(document_id=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
