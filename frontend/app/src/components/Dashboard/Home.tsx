"use client";
import dynamic from "next/dynamic";
import React, { useEffect, useState } from "react";
import ChartOne from "../Charts/ChartOne";
import ChartTwo from "../Charts/ChartTwo";
import ChatCard from "../Chat/ChatCard";
import TableOne from "../Tables/TableOne";
import CardDataStats from "../CardDataStats";
import { fetchDashboardData } from "@/utils/api";
import { formatDateTime, formatNumber } from "@/utils/func";
import { DashboardConfig } from "@/types/integration";
import Breadcrumb from "../Breadcrumbs/Breadcrumb";
import Toast from "../common/Toast";

const MapOne = dynamic(() => import("@/components/Maps/MapOne"), {
  ssr: false,
});

const ChartThree = dynamic(() => import("@/components/Charts/ChartThree"), {
  ssr: false,
});

const Home: React.FC = () => {
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<
    "success" | "error" | "warning" | "info"
  >("success");

  const [dashData, setDashData] = useState<DashboardConfig>({
    total_api_connections: 0,
    total_db_connections: 0,
    total_pipelines: 0,
    total_rows_migrated: 0,
    integrations: [],
  });
  const showToast = (
    message: string,
    type: "success" | "error" | "warning" | "info" = "success",
  ) => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await fetchDashboardData();
        setDashData(result);
      } catch (err: any) {
        showToast(
          err.message || "Failed to load data. Please try again.",
          "error",
        );
      }
    };

    loadData();
  }, []);

  const columns = [
    "Integration Name",
    "Run Count",
    "Latest Run Status",
    "Error Message",
    "Start Date",
    "End Date",
  ];

  return (
    <>
      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-6 xl:grid-cols-4 2xl:gap-7.5">
        <CardDataStats
          title="Total API Connections"
          total={`${dashData.total_api_connections}`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="size-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418"
            />
          </svg>
        </CardDataStats>
        <CardDataStats
          title="Total DB Connections"
          total={`${dashData.total_db_connections}`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="size-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125"
            />
          </svg>
        </CardDataStats>
        <CardDataStats
          title="Total Pipelines"
          total={`${dashData.total_pipelines}`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M10.5 6h-4.75M8.5 8.25a2.25 2.25 0 010-4.5M21 6h-7.5m3.5 6h4.75M16.5 9.75a2.25 2.25 0 010 4.5M3 12h7.5m-3.5 6h-4.75M8.5 18.25a2.25 2.25 0 010-4.5M21 18h-7.5"
            />
          </svg>
        </CardDataStats>
        <CardDataStats
          title="Total Rows Migrated"
          total={formatNumber(dashData.total_rows_migrated)}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 3h6v6H3V3zm12 0h6v6h-6V3zM3 15h6v6H3v-6zm12 0h6v6h-6v-6zM9 3h6v18H9V3z"
            />
          </svg>
        </CardDataStats>
      </div>

      {dashData.integrations.length > 0 && (
        <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
          <h2 className="mb-4 text-title-md2 font-semibold text-black dark:text-white">
            Integration Stats
          </h2>
          <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400 rtl:text-right">
            <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
              <tr>
                {columns.map((column, i) => (
                  <th key={i} scope="col" className="px-6 py-3">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dashData.integrations.map((integration, key) => (
                <tr
                  key={key}
                  className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600"
                >
                  <td className="px-6 py-4">{integration.integration_name}</td>
                  <td className="px-6 py-4">{integration.run_count}</td>
                  <td className="px-6 py-4">
                    <p
                      className={`inline-flex rounded-full bg-opacity-10 px-3 py-1 text-sm font-medium ${
                        integration.latest_run_status === "success"
                          ? "bg-success text-success"
                          : integration.latest_run_status === "running"
                            ? "bg-danger text-warning"
                            : "bg-danger text-danger"
                      }`}
                    >
                      {integration.latest_run_status}
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    {integration.error_message || "None"}
                  </td>
                  <td className="px-6 py-4">
                    {formatDateTime(integration.start_date)}
                  </td>
                  <td className="px-6 py-4">
                    {formatDateTime(integration.end_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Toast
        message={toastMessage}
        type={toastType}
        visible={toastVisible}
        onClose={() => setToastVisible(false)}
      />
    </>
  );
};

export default Home;
