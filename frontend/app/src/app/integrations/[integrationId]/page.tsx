"use client";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import Spinner from "@/components/common/Spinner";
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
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const load = async () => {
    setIsloading(true);
    const resp = await getIntegrationHistory(integrationId.toString(), page);
    setData(resp);
    setIsloading(false);
  };

  const changePage = (pg: number) => {
    setPage(pg);
  };

  useEffect(() => {
    document.title = "Integration History | OpenETL";

    load();
  }, [page]);

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
        <Breadcrumb
          pageName="Integration history"
          parentLink="/integrations"
          parentName="Integrations"
        />

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
            <nav
              className="flex-column flex flex-wrap items-center justify-between pt-4 md:flex-row"
              aria-label="Table navigation"
            >
              <span className="mb-4 block w-full text-sm font-normal text-gray-500 dark:text-gray-400 md:mb-0 md:inline md:w-auto">
                Total Pages:{" "}
                <span className="font-semibold text-gray-900 dark:text-white">
                  {data.total_pages}
                </span>
              </span>
              <span className="mb-4 block w-full text-sm font-normal text-gray-500 dark:text-gray-400 md:mb-0 md:inline md:w-auto">
                Total Items:{" "}
                <span className="font-semibold text-gray-900 dark:text-white">
                  {data.total_items}
                </span>
              </span>
              <ul className="inline-flex h-8 -space-x-px text-sm rtl:space-x-reverse">
                {data.page !== 1 && (
                  <li>
                    <button
                      onClick={() => changePage(data.page - 1)}
                      className="ms-0 flex h-8 items-center justify-center rounded-s-lg border border-gray-300 bg-white px-3 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                    >
                      Previous
                    </button>
                  </li>
                )}
                <li>
                  <span
                    aria-current="page"
                    className="flex h-8 items-center justify-center border border-gray-300 bg-blue-50 px-3 text-blue-600 hover:bg-blue-100 hover:text-blue-700 dark:border-gray-700 dark:bg-gray-700 dark:text-white"
                  >
                    {data.page}
                  </span>
                </li>
                {data.page !== data.total_pages && (
                  <li>
                    <button
                      onClick={() => changePage(data.page + 1)}
                      className="flex h-8 items-center justify-center rounded-e-lg border border-gray-300 bg-white px-3 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                    >
                      Next
                    </button>
                  </li>
                )}
              </ul>
            </nav>
          </div>
        ) : (
          <div
            className="mb-4 rounded-lg bg-gray-200 p-4 text-sm dark:bg-gray-800"
            role="alert"
          >
            <span className="font-medium">Oops!</span> No records found!
          </div>
        )}
        <Spinner visible={isLoading} />
      </DefaultLayout>
    </>
  );
};

export default IntegrationHistory;
