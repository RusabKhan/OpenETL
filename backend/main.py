from fastapi import FastAPI
import os
import sys

from utils.database_utils import DatabaseUtils
from utils.spark_utils import print_iam_alive

sys.path.append(os.environ['OPENETL_HOME'])
from app.database import router as db_router
from app.connector import router as connector_router
from fastapi.responses import ORJSONResponse
from utils.__migrations__.app import OpenETLDocument
from utils.__migrations__.scheduler import OpenETLIntegrations


def __init__():
    db_class = DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
              hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
              port=os.getenv('OPENETL_DOCUMENT_PORT'),
              username=os.getenv('OPENETL_DOCUMENT_USER'),
              password=os.getenv('OPENETL_DOCUMENT_PASS'),
              database=os.getenv('OPENETL_DOCUMENT_DB'))
    db_class.create_table_from_base(base=OpenETLDocument)
    db_class.create_table_from_base(base=OpenETLIntegrations)
    print_iam_alive.apply_async(countdown=5)  # Scheduled task






app = FastAPI(default_response_class=ORJSONResponse, on_startup=[__init__])

app.include_router(db_router)
app.include_router(connector_router)



