from datetime import datetime

from sqlalchemy import Column, Integer, UUID, DateTime, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class OpenETLBatch(Base):
    __tablename__ = 'openetl_batches'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(UUID(as_uuid=True))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    batch_type = Column(String)
    batch_status = Column(String)
    integration_name = Column(String)
    integration_id = Column(String)
    rows_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
