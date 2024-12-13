from pydantic import BaseModel, Field, constr
from uuid import UUID
from typing import List, Optional
import datetime

from utils.enums import IntegrationType


class CreatePipelineModel(BaseModel):
    spark_config: dict = Field(..., min_length=0,  examples=[{"spark.driver.memory": "1g"}, None])
    hadoop_config: dict = Field(..., min_length=0,  examples=[{"dfs.replication": "1"}, None])
    integration_name: str = Field(..., min_length=3,  examples=["demo"])
    integration_type: str = Field(..., min_length=3,  examples=["full load"])
    target_table: str = Field(..., min_length=3,  examples=["target_table"])
    source_table: str = Field(..., min_length=3,  examples=["source_table"])
    target_schema: str = Field(..., min_length=3,  examples=["target_schema"])
    source_schema: str = Field(..., min_length=3,  examples=["source_schema"])
    target_connection: int = Field(...,  examples=["target_connection_name"])
    source_connection: int = Field(...,  examples=["source_connection_name"])
    schedule_date: list[str] = Field(...,  examples=["2023-01-01"])
    schedule_time: str = Field(..., min_length=3,  examples=["00:00:00"])
    frequency: str = Field(..., min_length=3,  examples=["daily"])
    batch_size: int = Field(...,  examples=["100000"])


class IntegrationBody(BaseModel):
    id: Optional[UUID] = Field(default=None)  # Unique identifier
    integration_name: Optional[constr(min_length=1)] = Field(None, description="Name of the integration")
    integration_type: Optional[IntegrationType] = Field(None, description="Type of integration (e.g., API, DB)")
    cron_expression: Optional[List[str]] = Field(None, description="Cron schedule for periodic tasks")
    source_connection: Optional[UUID] = Field(None, description="Source connection identifier")
    target_connection: Optional[UUID] = Field(None, description="Target connection identifier")
    spark_config: Optional[dict] = Field(None, description="Spark configuration (optional)")
    hadoop_config: Optional[dict] = Field(None, description="Hadoop configuration (optional)")
    batch_size: Optional[int] = Field(None, description="Batch size for processing")
    source_table: Optional[constr(min_length=1)] = Field(None, description="Source table name")
    target_table: Optional[constr(min_length=1)] = Field(None, description="Target table name")
    source_schema: Optional[constr(min_length=1)] = Field(None, description="Source schema name")
    target_schema: Optional[constr(min_length=1)] = Field(None, description="Target schema name")
    is_enabled: Optional[bool] = Field(None, description="Indicates whether the scheduler is enabled")
    is_running: Optional[bool] = Field(None, description="Indicates whether the scheduler is currently running")
    created_at: Optional[datetime] = Field(None, description="Record creation time (auto-generated)")
    updated_at: Optional[datetime] = Field(None, description="Record update time (auto-generated)")