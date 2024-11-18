from fastapi import APIRouter, Body, FastAPI, HTTPException, Request
import os
import sys

from utils.connector_utils import get_installed_connectors
from utils.enums import AuthType, ConnectionType
from utils.generic_utils import get_open_etl_document_connection_details
sys.path.append(os.environ['OPENETL_HOME'])
from utils.database_utils import DatabaseUtils
import utils.connector_utils as con_utils

router = APIRouter(prefix="/connector", tags=["connector"])


@router.get("/get_installed_connectors")
async def get_installed_connectors_api():
    database_sources = get_installed_connectors(ConnectionType.DATABASE)
    api_engines = get_installed_connectors(ConnectionType.API)
    return {"database": database_sources, "api": api_engines}


@router.post("/test_connection")
async def test_connection_api(request: Request, connector_name: str = Body(...), connector_type: str = Body(...), auth_type: str = Body(...), auth_params: dict = Body(...)):
    return con_utils.connector_test_connection(connector_name, ConnectionType(connector_type), auth_type, **auth_params)


@router.post("/store_connection")
async def store_connection_api(request: Request, connection_credentials: dict = Body(...), connection_name: str = Body(...), connection_type: str = Body(...), connector_name: str = Body(...), auth_type: str = Body(...)):
    vals = get_open_etl_document_connection_details()
    auth_type = AuthType(auth_type)
    data = {"connection_credentials": connection_credentials, "connection_name": connection_name, "connection_type": connection_type, "auth_type": auth_type, "connector_name": connector_name}
    return DatabaseUtils(**vals).write_document(data)
    
    
@router.get("/get_connector_auth_details/{connector_name}/{connector_type}")
async def get_connector_auth_details_api(request: Request, connector_name: str, connector_type: str):
    connector_type = ConnectionType(connector_type)
    return con_utils.get_connector_auth_details(connector_name, connector_type)


@router.get("/get_connector_image/{connector_name}/{connector_type}")
async def get_connector_image_api(request: Request, connector_name: str, connector_type: str):
    return con_utils.get_connector_image(connector_name,connector_type)
