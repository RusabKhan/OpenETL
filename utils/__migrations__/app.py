from datetime import datetime

from sqlalchemy import Column, Integer, JSON, String, Enum, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from utils.enums import AuthType

Base = declarative_base()


class OpenETLDocument(Base):
    __tablename__ = 'openetl_documents'
    __table_args__ = {'schema': 'public'}

    document_id = Column(Integer, primary_key=True)
    connection_credentials = Column(JSON)
    connection_name = Column(String, unique=True)
    connection_type = Column(String)
    auth_type = Column(Enum(AuthType))
    connector_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class OpenETLBatch(Base):
    __tablename__ = 'openetl_batches'
    __table_args__ = {'schema': 'public'}

    uid = Column(Integer, primary_key=True)
    batch_id = Column(UUID(as_uuid=True))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    batch_type = Column(String)
    batch_status = Column(String)
    integration_name = Column(String)
    rows_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
