from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UUID, Boolean, Text, ForeignKey
from .app import OpenETLDocument
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OpenETLScheduler(Base):
    __tablename__ = 'openetl_scheduler'
    __table_args__ = {'schema': 'public'}

    uid = Column(UUID, primary_key=True, autoincrement=True)  # Unique identifier
    integration_name = Column(String, nullable=False)  # Name of the integration
    integration_type = Column(String, nullable=False)  # Type of integration (e.g., API, DB)
    cron_expression = Column(String, nullable=False)  # Cron schedule for periodic tasks
    source_connection = Column(ForeignKey(OpenETLDocument.document_id), nullable=False)  # Source table name
    target_connection = Column(ForeignKey(OpenETLDocument.document_id), nullable=False)  # Target table name
    source_table = Column(String, nullable=False)  # Source table name
    target_table = Column(String, nullable=False)  # Target table name
    integration_status = Column(String, nullable=False, default="inactive")  # Status (active/inactive)
    last_run_status = Column(String, nullable=True)  # Status of the last run (success/failure)
    start_date = Column(DateTime, nullable=True)  # Scheduled start date
    end_date = Column(DateTime, nullable=True)  # Scheduled end date
    next_run_time = Column(DateTime, nullable=True)  # Next scheduled run
    last_run_time = Column(DateTime, nullable=True)  # Time of the last run
    error_message = Column(Text, nullable=True)  # Error message, if the last run failed
    is_enabled = Column(Boolean, default=True)  # Indicates whether the scheduler is enabled
    is_running = Column(Boolean, default=False)  # Indicates whether the scheduler is currently running
    created_at = Column(DateTime, default=datetime.utcnow)  # Record creation time
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Record update time