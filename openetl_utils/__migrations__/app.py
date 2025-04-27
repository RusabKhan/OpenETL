from datetime import datetime

from sqlalchemy import Column, Integer, JSON, String, Enum, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from openetl_utils.enums import AuthType

Base = declarative_base()


class OpenETLDocument(Base):
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
