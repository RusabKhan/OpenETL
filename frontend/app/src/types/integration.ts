export type SparkConfig = {
  [key: string]: string;
};

export type HadoopConfig = {
  [key: string]: string;
};

export type IntegrationConfig = {
  frequency: string; // e.g., "Weekly"
  hadoop_config: HadoopConfig; // Hadoop configuration details
  integration_name: string; // e.g., ""
  integration_type: string; // e.g., "full_load"
  schedule_date: string[]; // Array of dates in "YYYY-MM-DD" format
  schedule_time: string; // Time in "HH:mm:ss" format
  source_connection: number; // ID or identifier for the source connection
  source_schema: string; // e.g., "public"
  source_table: string; // e.g., ""
  spark_config: SparkConfig; // Spark configuration details
  target_connection: number; // ID or identifier for the target connection
  target_schema: string; // e.g., "public"
  target_table: string; // e.g., ""
  batch_size: number; // e.g., 100000
};
