import axios from "axios";

// Define the base URL globally for reuse
export const base_url = process.env.NEXT_PUBLIC_API_URL;

export const fetchDashboardData = async () => {
  try {
    const response = await axios.get(`${base_url}/database/get_dashboard_data`);
    return response.data;
  } catch (error: any) {
    console.error("Error fetching dashboard data:", error.message);
    throw new Error(
      error.response?.data?.message || "Error fetching dashboard data",
    );
  }
};

export const fetchInstalledConnectors = async (type: string) => {
  try {
    let response = await axios.post(
      `${base_url}/connector/get_created_connections`,
      {
        connector_type: type,
      },
    );

    return response.data;
  } catch (error: any) {
    console.error("Error fetching connector details:", error.message);
    throw new Error(
      error.response?.data?.message || "Error fetching connector details",
    );
  }
};
