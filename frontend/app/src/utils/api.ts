import {
  ParamMetadata,
  ParamUpdateConnection,
  StoreConnectionsParam,
  TestConnection,
} from "@/types/connectors";
import {
  IntegrationConfig,
  LogsParam,
  ParamUpdateIntegration,
} from "@/types/integration";
import axios from "axios";

// Define the base URL globally for reuse
export const base_url = process.env.NEXT_PUBLIC_API_URL;

// Generic API handler
const apiRequest = async (
  method: "get" | "post" | "put" | "delete",
  endpoint: string,
  data?: object,
) => {
  try {
    const config = {
      method,
      url: `${base_url}${endpoint}`,
      ...(data && { data }),
    };

    const response = await axios(config);
    return response.data;
  } catch (error: any) {
    console.error(
      `Error in API request: ${method.toUpperCase()} ${endpoint}`,
      error.message,
    );
    throw new Error(
      error.response?.data?.message ||
        `Error occurred during ${method.toUpperCase()} ${endpoint}`,
    );
  }
};

// GET
export const fetchDashboardData = async () => {
  return apiRequest("get", "/database/get_dashboard_data");
};
export const fetchInstalledConnectors = async () => {
  return apiRequest("get", "/connector/get_installed_connectors");
};
export const getConnectorAuthDetails = async (name: string, type: string) => {
  return apiRequest(
    "get",
    `/connector/get_connector_auth_details/${name}/${type}`,
  );
};
export const getIntegrations = async () => {
  return apiRequest("get", "/pipeline/get_integrations");
};
export const getIntegrationHistory = async (id: string) => {
  return apiRequest("get", `/pipeline/get_integration_history/${id}`);
};
export const getPipelineLogs = async (params: LogsParam) => {
  return apiRequest(
    "get",
    `/pipeline/get_logs?${params.integration_id ? `integration_id=${params.integration_id}&logs_type=${params.logs_type}` : `logs_type=${params.logs_type}`}&page=${params.page}&per_page=${params.per_page}`,
  );
};

// POST
export const fetchCreatedConnections = async (type: string) => {
  return apiRequest("post", "/connector/get_created_connections", {
    connector_type: type,
  });
};
export const test_connection = async (params: TestConnection) => {
  return apiRequest("post", "/connector/test_connection", {
    ...params,
  });
};
export const store_connection = async (params: StoreConnectionsParam) => {
  return apiRequest("post", "/connector/store_connection", {
    ...params,
  });
};
export const fetch_metadata = async (params: ParamMetadata) => {
  return apiRequest("post", "/connector/fetch_metadata", {
    ...params,
  });
};
export const create_integration = async (params: IntegrationConfig) => {
  return apiRequest("post", "/pipeline/create_integration", {
    ...params,
  });
};

// DELETE
export const delete_connection = async (id: number) => {
  return apiRequest(
    "delete",
    `/connector/delete_connection/?document_id=${id}`,
  );
};

// UPDATE
export const update_connection = async (params: ParamUpdateConnection) => {
  return apiRequest("post", "/connector/update_connection", params);
};
export const update_integration = async (params: ParamUpdateIntegration) => {
  return apiRequest("post", "/pipeline/update_integration", params);
};
