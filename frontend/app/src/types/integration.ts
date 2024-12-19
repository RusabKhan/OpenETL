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

export type ListIntegrationConfig = {
  id: string;
  integration_name: string;
  integration_type: string;
  cron_expression: string[];
  is_running: boolean;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
  history: [];
};

export type PaginatedIntegrationConfig = {
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  data?: ListIntegrationConfig[];
};

export type ParamUpdateIntegration = {
  pipeline_id: string;
  fields: {
    [key: string]: string;
  };
};