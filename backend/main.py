from fastapi import Body, FastAPI, HTTPException, Request
import os
import sys

from utils.database_utils import DatabaseUtils

sys.path.append(os.environ['OPENETL_HOME'])
from .database import router as db_router
from .connector import router as connector_router
from fastapi.responses import ORJSONResponse
from .__migrations__.app import OpenETLDocument
from .__migrations__.scheduler import OpenETLScheduler

def __init__():
    db_class = DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
              hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
              port=os.getenv('OPENETL_DOCUMENT_PORT'),
              username=os.getenv('OPENETL_DOCUMENT_USER'),
              password=os.getenv('OPENETL_DOCUMENT_PASS'),
              database=os.getenv('OPENETL_DOCUMENT_DB'))
    db_class.create_table_from_base(base=OpenETLDocument)
    db_class.create_table_from_base(base=OpenETLScheduler)

app = FastAPI(default_response_class=ORJSONResponse, on_startup=[__init__])

app.include_router(db_router)
app.include_router(connector_router)



