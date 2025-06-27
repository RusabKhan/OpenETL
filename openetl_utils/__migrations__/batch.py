from datetime import datetime

from sqlalchemy import Column, Integer, UUID, DateTime, String, Enum
from sqlalchemy.orm import declarative_base
from openetl_utils.enums import RunStatus

Base = declarative_base()

class OpenETLBatch(Base):
    __tablename__ = 'openetl_batches'

    id = Column(Integer, primary_key=True, autoincrement=False)
    batch_id = Column(String(36), unique=True, nullable=False)
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

    def __init__(self, uid, batch_id, run_id, start_date, end_date, batch_type, batch_status, integration_name, integration_id, rows_count):
        self.id = uid
        self.batch_id = batch_id
        self.run_id = run_id
        self.start_date = start_date
        self.end_date = end_date
        self.batch_type = batch_type
        self.batch_status = batch_status
        self.integration_name = integration_name
        self.integration_id = integration_id
        self.rows_count = rows_count

