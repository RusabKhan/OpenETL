from fastapi import APIRouter, Body, FastAPI, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from cachetools import TTLCache
import os
import sys

sys.path.append(os.environ['OPENETL_HOME'])
from utils.database_utils import DatabaseUtils



router = APIRouter(prefix="/database", tags=["database"])


@router.get("/get_dashboard_data")
async def get_dashboard_data_api(request: Request):
    return  DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
                hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
                port=os.getenv('OPENETL_DOCUMENT_PORT'),
                username=os.getenv('OPENETL_DOCUMENT_USER'),
                password=os.getenv('OPENETL_DOCUMENT_PASS'),
                database=os.getenv('OPENETL_DOCUMENT_DB')).get_dashboard_data()


