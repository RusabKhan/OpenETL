"use client";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { PaginatedIntegrationHistoryConfig } from "@/types/integration";
import { getIntegrationHistory } from "@/utils/api";
import { formatDateTime } from "@/utils/func";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

const IntegrationHistory = () => {
  const { integrationId } = useParams();
  const [data, setData] = useState<PaginatedIntegrationHistoryConfig>();

  const load = async () => {
    const resp = await getIntegrationHistory(integrationId.toString());
    setData(resp);
  };

  useEffect(() => {
    load();
  }, []);

  const columns = [
    "Id",
    "Integration Id",
    "Run Status",
    "Row Count",
    "Error Message",
    "Start Date",
    "End Date",
    "Created At",
    "Updated At",
  ];

  return (
    <>
      <DefaultLayout>
        <Breadcrumb pageName="Integration history" />

        {data?.data && data?.data?.length > 0 ? (
          <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
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
                {data?.data?.map((integration, key) => (
                  <tr
                    key={key}
                    className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600"
                  >
                    <td className="px-6 py-4">{integration.id}</td>
                    <td className="px-6 py-4">{integration.integration}</td>
                    <td className="px-6 py-4">
                      <p
                        className={`inline-flex rounded-full bg-opacity-10 px-3 py-1 text-sm font-medium ${
                          integration.run_status === "success"
                            ? "bg-success text-success"
                            : integration.run_status === "running"
                              ? "bg-danger text-warning"
                              : "bg-danger text-danger"
                        }`}
                      >
                        {integration.run_status}
                      </p>
                    </td>
                    <td className="px-6 py-4">{integration.row_count}</td>
                    <td className="px-6 py-4">{integration.error_message}</td>
                    <td className="px-6 py-4">
                      {formatDateTime(integration.start_date)}
                    </td>
                    <td className="px-6 py-4">
                      {formatDateTime(integration.end_date)}
                    </td>
                    <td className="px-6 py-4">
                      {formatDateTime(integration.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      {formatDateTime(integration.updated_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div
            className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-800 dark:bg-gray-800 dark:text-red-400"
            role="alert"
          >
            <span className="font-medium">Oops!</span> No records found!
          </div>
        )}
      </DefaultLayout>
    </>
  );
};

export default IntegrationHistory;
