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
import axios, { AxiosRequestConfig, Canceler } from "axios";

// Define the base URL globally for reuse
export const base_url = process.env.NEXT_PUBLIC_API_URL;

// Generic API handler
const pendingRequests = new Map<string, Canceler>();

const apiRequest = async (
  method: "get" | "post" | "put" | "delete",
  endpoint: string,
  data?: object,
) => {
  const url = `${base_url}${endpoint}`;

  // Create a unique key for each request
  const requestKey = `${method.toUpperCase()}::${url}`;

  // Cancel any previous request with the same key
  if (pendingRequests.has(requestKey)) {
    const cancel = pendingRequests.get(requestKey);
    cancel?.("Request canceled due to a new request with the same key.");
    pendingRequests.delete(requestKey);
  }

  // Create a CancelToken
  const cancelToken = new axios.CancelToken((canceler) => {
    pendingRequests.set(requestKey, canceler);
  });

  try {
    const config: AxiosRequestConfig = {
      method,
      url,
      ...(data && { data }),
      cancelToken,
    };

    const response = await axios(config);

    // Remove the request key after a successful response
    pendingRequests.delete(requestKey);

    return response.data;
  } catch (error: any) {
    // Remove the request key on error
    pendingRequests.delete(requestKey);

    if (axios.isCancel(error)) {
      console.warn(`Request canceled: ${requestKey}`, error.message);
      throw new Error("Request was canceled.");
    }

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
export const getIntegrations = async (page?: number) => {
  return apiRequest("get", `/pipeline/get_integrations?page=${page}`);
};
export const getIntegrationHistory = async (id: string, page: number) => {
  return apiRequest("get", `/pipeline/get_integration_history/${id}?page=${page}`);
};
export const getPipelineLogs = async (params: LogsParam) => {
  return apiRequest(
    "get",
    `/pipeline/get_logs?${params.integration_id ? `integration_id=${params.integration_id}&logs_type=${params.logs_type}` : `logs_type=${params.logs_type}`}&page=${params.page}&per_page=${params.per_page}`,
  );
};
export const getSchedulerListJobs = async () => {
  return apiRequest("get", "/scheduler/list-jobs");
};
export const getCeleryTasks = async () => {
  return apiRequest("get", "/worker/tasks");
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
