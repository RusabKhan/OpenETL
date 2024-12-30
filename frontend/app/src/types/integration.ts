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
  cron_expression: string;
  is_running: boolean;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
};

export type PaginatedIntegrationConfig = {
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  data?: ListIntegrationConfig[];
};

export type ListIntegrationHistoryConfig = {
  id: string;
  integration: string;
  run_status: string;
  row_count: string;
  error_message: string;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
};

export type PaginatedIntegrationHistoryConfig = {
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  data?: ListIntegrationHistoryConfig[];
};

export type ParamUpdateIntegration = {
  pipeline_id: string;
  fields: {
    [key: string]: string;
  };
};

export type DashboardIntegrationConfig = {
  integration_name: string;
  run_count: string;
  latest_run_status: string;
  error_message?: string;
  start_date: string;
  end_date: string;
};

export type DashboardConfig = {
  total_api_connections: number;
  total_db_connections: number;
  total_pipelines: number;
  total_rows_migrated: number;
  integrations: DashboardIntegrationConfig[];
}