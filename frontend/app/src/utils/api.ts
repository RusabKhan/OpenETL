import {
  ParamMetadata,
  StoreConnectionsParam,
  TestConnection,
} from "@/types/connectors";
import { IntegrationConfig } from "@/types/integration";
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
