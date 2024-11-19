from fastapi import Body, FastAPI, HTTPException, Request
import os
import sys
sys.path.append(os.environ['OPENETL_HOME'])
from .database import router as db_router
from .connector import router as connector_router

# Define the SQLAlchemy models
# FastAPI app
app = FastAPI()
app.include_router(db_router)
app.include_router(connector_router)

