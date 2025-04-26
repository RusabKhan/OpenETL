import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UUID, Boolean, Text, ForeignKey, LargeBinary, Enum, JSON, \
    ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from .app import OpenETLDocument
from sqlalchemy.ext.declarative import declarative_base

from openetl_utils.enums import RunStatus, IntegrationType

Base = declarative_base()


class OpenETLIntegrations(Base):
    __tablename__ = 'openetl_integrations'
    __table_args__ = {'schema': 'public'}

    id = Column(UUID, primary_key=True, default=uuid.uuid4)  # Unique identifier
    integration_name = Column(String, nullable=False, unique=True)  # Name of the integration
    integration_type = Column(Enum(IntegrationType), nullable=False)  # Type of integration (e.g., API, DB)
    cron_expression = Column(ARRAY(String), nullable=False)  # Cron schedule for periodic tasks
    source_connection = Column(ForeignKey(OpenETLDocument.id), nullable=False)  # Source table name
    target_connection = Column(ForeignKey(OpenETLDocument.id), nullable=False)  # Target table name
    spark_config = Column(JSON, nullable=True)
    hadoop_config = Column(JSON, nullable=True)
    batch_size = Column(Integer, nullable=False, default=100000)
    source_table = Column(String, nullable=False)  # Source table name
    target_table = Column(String, nullable=False)  # Target table name
    source_schema = Column(String, nullable=False)  # Source schema name
    target_schema = Column(String, nullable=False)  # Target schema name
    is_enabled = Column(Boolean, default=True)  # Indicates whether the scheduler is enabled
    is_running = Column(Boolean, default=False)  # Indicates whether the scheduler is currently running
    created_at = Column(DateTime, default=datetime.utcnow)  # Record creation time
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Record update time

class OpenETLIntegrationsRuntimes(Base):
    __tablename__ = 'openetl_integrations_history'
    __table_args__ = {'schema': 'public'}

    id = Column(UUID, primary_key=True, default=uuid.uuid4)  # Unique identifier
    integration = Column(ForeignKey(OpenETLIntegrations.id), nullable=False)  # Name of the integration
    created_at = Column(DateTime, default=datetime.utcnow)  # Record creation time
    error_message = Column(Text, nullable=True)  # Error message, if the last run failed
    run_status = Column(Enum(RunStatus), nullable=True)  # Status of the last run (success/failure)
    start_date = Column(DateTime, nullable=True)  # Scheduled start date
    celery_task_id = Column(String, nullable=True)  # Celery task ID
    end_date = Column(DateTime, nullable=True)  # Scheduled end date
    row_count = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

