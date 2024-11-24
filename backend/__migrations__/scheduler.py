from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OpenETLScheduler(Base):
    __tablename__ = 'openetl_scheduler'
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