from fastapi import Body, FastAPI, HTTPException, Request
import os
import sys

from utils.database_utils import DatabaseUtils

sys.path.append(os.environ['OPENETL_HOME'])
from .database import router as db_router
from .connector import router as connector_router
from fastapi.responses import ORJSONResponse
# Define the SQLAlchemy models
# FastAPI app


app = FastAPI(default_response_class=ORJSONResponse)

app.include_router(db_router)
app.include_router(connector_router)

app.on_event("startup")
def create_document_table():
    DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
              hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
              port=os.getenv('OPENETL_DOCUMENT_PORT'),
              username=os.getenv('OPENETL_DOCUMENT_USER'),
              password=os.getenv('OPENETL_DOCUMENT_PASS'),
              database=os.getenv('OPENETL_DOCUMENT_DB')).create_document_table()

