from pydantic import BaseModel, Field


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
