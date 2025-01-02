import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UUID, Boolean, Text, ForeignKey, LargeBinary, Enum, JSON, \
    ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from .app import OpenETLDocument
from sqlalchemy.ext.declarative import declarative_base

from utils.enums import RunStatus, IntegrationType

Base = declarative_base()


class OpenETLIntegrations(Base):
    """
    Represents the 'openetl_integrations' table in the database, storing integration configurations.

    Attributes:
        id (UUID): Unique identifier for the integration.
        integration_name (str): Unique name of the integration.
        integration_type (IntegrationType): Type of integration (e.g., API, DB).
        cron_expression (list of str): Cron schedule for periodic tasks.
        source_connection (int): Foreign key referencing the source connection.
        target_connection (int): Foreign key referencing the target connection.
        spark_config (dict): JSON configuration for Spark.
        hadoop_config (dict): JSON configuration for Hadoop.
        batch_size (int): Number of records to process in each batch.
        source_table (str): Name of the source table.
        target_table (str): Name of the target table.
        source_schema (str): Name of the source schema.
        target_schema (str): Name of the target schema.
        is_enabled (bool): Indicates if the scheduler is enabled.
        is_running (bool): Indicates if the scheduler is currently running.
        created_at (datetime): Timestamp of when the record was created.
        updated_at (datetime): Timestamp of when the record was last updated.
    """
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
    """
    Represents the runtime history of OpenETL integrations.

    Attributes:
        id (UUID): Unique identifier for the runtime record.
        integration (UUID): Foreign key referencing the OpenETL integration.
        created_at (DateTime): Timestamp of when the record was created.
        error_message (Text): Error message if the last run failed.
        run_status (RunStatus): Status of the last run (e.g., success, failure).
        start_date (DateTime): Scheduled start date of the integration run.
        celery_task_id (String): Identifier for the associated Celery task.
        end_date (DateTime): Scheduled end date of the integration run.
        row_count (Integer): Number of rows processed in the run.
        updated_at (DateTime): Timestamp of the last update to the record.
    """
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

