from datetime import datetime

from sqlalchemy import Column, Integer, JSON, String, Enum, DateTime, UUID, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from utils.enums import AuthType

Base = declarative_base()


class OpenETLDocument(Base):
    """
    Represents the 'openetl_documents' table in the database. Stores connection details.

    Attributes:
        id (int): Primary key, auto-incremented.
        connection_credentials (dict): JSON field for storing connection credentials.
        connection_name (str): Unique name for the connection.
        connection_type (str): Type of the connection.
        auth_type (AuthType): Enum indicating the authentication type.
        connector_name (str): Name of the connector.
        created_at (datetime): Timestamp of when the record was created.
        updated_at (datetime): Timestamp of when the record was last updated.
    """
    __tablename__ = 'openetl_documents'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_credentials = Column(JSON)
    connection_name = Column(String, unique=True)
    connection_type = Column(String)
    auth_type = Column(Enum(AuthType))
    connector_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class OpenETLBatch(Base):
    """
    Represents the 'openetl_batches' table in the database. Stores batch processing details on target end.

    Attributes:
        id (int): Primary key, auto-incremented.
        batch_id (UUID): Unique identifier for the batch.
        start_date (datetime): Start date of the batch process.
        end_date (datetime): End date of the batch process.
        batch_type (str): Type of the batch.
        batch_status (str): Current status of the batch.
        integration_name (str): Name of the integration associated with the batch.
        rows_count (int): Number of rows processed, default is 0.
        created_at (datetime): Timestamp of when the record was created.
        updated_at (datetime): Timestamp of when the record was last updated.
    """
    __tablename__ = 'openetl_batches'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
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


class OpenETLOAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    connection = Column(ForeignKey(OpenETLDocument.id), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expiry_time = Column(DateTime, nullable=False)
    scope = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
