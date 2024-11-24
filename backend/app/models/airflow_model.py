from pydantic import BaseModel, Field


class CreatePipelineModel(BaseModel):
    spark_config: dict = Field(..., min_length=3, max_length=50, examples=[{"spark.driver.memory": "1g"}, None])
    hadoop_config: dict = Field(..., min_length=3, max_length=50, examples=[{"dfs.replication": "1"}, None])
    integration_name: str = Field(..., min_length=3, max_length=50, examples=["demo"])
    is_frequency: bool = Field(..., min_length=3, max_length=50, examples=[False, True])
    selected_dates: list | None = Field(..., min_length=3, max_length=50, examples=["2023-01-01", "2023-01-02"])
    schedule_time: str | None = Field(..., min_length=3, max_length=50, examples=["00:00:00"])
    frequency: str | None = Field(..., min_length=0, max_length=50, examples=["Weekly"])
    schedule_dates: str | None = Field(..., min_length=3, max_length=50, examples=["2023-01-01"])
    run_details: dict | None | {} = Field(..., min_length=3, max_length=50, examples=[{"2023-01-01": {"rows_read": 0,
                                                                                                      "rows_write": 0,
                                                                                                      "start_time": "00:00:00",
                                                                                                      "end_time": "00:00:00",
                                                                                                      "status": "Not Started"}},
                                                                                                            None, {}])
    target_table: str = Field(..., min_length=3, max_length=50, examples=["target_table"])
    source_table: str = Field(..., min_length=3, max_length=50, examples=["source_table"])
    target_schema: str = Field(..., min_length=3, max_length=50, examples=["target_schema"])
    source_schema: str = Field(..., min_length=3, max_length=50, examples=["source_schema"])
    target_connection_name: str = Field(..., min_length=3, max_length=50, examples=["target_connection_name"])
    source_connection_name: str = Field(..., min_length=3, max_length=50, examples=["source_connection_name"])
    target_type: str = Field(..., min_length=3, max_length=50, examples=["target_type"])
    source_type: str = Field(..., min_length=3, max_length=50, examples=["source_type"])
