from fastapi import FastAPI
import os
import sys
from fastapi.middleware.cors import CORSMiddleware

from app.middlewares.exception_handler import ExceptionHandlingMiddleware
from app.middlewares.response_status import StatusAdjustMiddleware
from openetl_utils.database_utils import DatabaseUtils

sys.path.append(os.environ['OPENETL_HOME'])
from app.database import router as db_router
from app.connector import router as connector_router
from app.worker import router as celery_router
from app.scheduler import router as scheduler_router
from app.pipeline import router as pipeline_router
from app.oauth import router as oauth_router
from app.middlewares.logging import LoggingMiddleware
from fastapi.responses import ORJSONResponse
from openetl_utils.__migrations__.app import OpenETLDocument, OpenETLOAuthToken
from openetl_utils.__migrations__.scheduler import OpenETLIntegrations, OpenETLIntegrationsRuntimes


def __init__():
    db_class = DatabaseUtils(engine=os.getenv('OPENETL_DOCUMENT_ENGINE'),
              hostname=os.getenv('OPENETL_DOCUMENT_HOST'),
              port=os.getenv('OPENETL_DOCUMENT_PORT'),
              username=os.getenv('OPENETL_DOCUMENT_USER'),
              password=os.getenv('OPENETL_DOCUMENT_PASS'),
              database=os.getenv('OPENETL_DOCUMENT_DB'))
    db_class.create_table_from_base(base=OpenETLDocument)
    db_class.create_table_from_base(base=OpenETLIntegrations)
    db_class.create_table_from_base(base=OpenETLIntegrationsRuntimes)
    db_class.create_table_from_base(base=OpenETLOAuthToken)


app = FastAPI(default_response_class=ORJSONResponse, on_startup=[__init__])

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://frontend:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(StatusAdjustMiddleware)
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(LoggingMiddleware)


app.include_router(db_router)
app.include_router(connector_router)
app.include_router(celery_router)
app.include_router(pipeline_router)
app.include_router(oauth_router)
app.include_router(scheduler_router)


