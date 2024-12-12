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

export const fetchDashboardData = async () => {
  return apiRequest("get", "/database/get_dashboard_data");
};

export const fetchCreatedConnections = async (type: string) => {
  return apiRequest("post", "/connector/get_created_connections", {
    connector_type: type,
  });
};

export const fetchInstalledConnectors = async () => {
  return apiRequest("get", "/connector/get_installed_connectors")
};
