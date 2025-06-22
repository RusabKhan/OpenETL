from datetime import datetime

from sqlalchemy import Column, Integer, UUID, DateTime, String, Enum
from sqlalchemy.orm import declarative_base
from openetl_utils.enums import RunStatus

Base = declarative_base()

class OpenETLBatch(Base):
    __tablename__ = 'openetl_batches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(36))
    run_id = Column(String(36))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    batch_type = Column(String(50))
    batch_status = Column(Enum(RunStatus))
    integration_name = Column(String(500))
    integration_id = Column(String(500))
    rows_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
