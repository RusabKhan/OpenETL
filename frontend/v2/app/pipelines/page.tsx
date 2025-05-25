"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Spinner from "@/components/Spinner";
import { PaginatedIntegrationConfig } from "@/components/types/integration";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import ETLTable from "@/components/ui/etl-table";
import { getIntegrations } from "@/components/utils/api";
import { IconRefresh } from "@tabler/icons-react";
import { PlusIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

const initial_list = {
  page: 1,
  per_page: 10,
  total_items: 1,
  total_pages: 1,
  data: [],
};

export default function PipelinesPage() {
  const [integrations, setIntegrations] =
    useState<PaginatedIntegrationConfig>(initial_list);
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const load_integrations = async (cache: boolean) => {
    setIsloading(true);
    const response = await getIntegrations(cache, page);
    setIntegrations(response.data);
    setIsloading(false);
  };

  const router = useRouter();

  const changePage = (pg: number) => {
    setPage(pg);
  };

  useEffect(() => {
    document.title = "Pipelines | OpenETL";
    
    load_integrations(true);
  }, [page]);

  const columns = ["Id", "Name", "Type", "Cron Expression", "Active", "Status"];

  return (
    <DefaultLayout title="Pipelines">
      <div className="relative p-4 md:p-6">
        <div className="absolute top-4 right-4 md:top-4 md:right-6 z-10">
          <button
            className="cursor-pointer inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm bg-gray-800 hover:bg-gray-700 dark:bg-gray-200 dark:text-gray-900 dark:hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            onClick={() => router.push("/pipelines/create")}
          >
            <PlusIcon /> Create ETL Pipeline
          </button>
        </div>
        <h1 className="flex items-center gap-4 text-2xl font-bold mb-6">
          Pipelines{" "}
          <button
            className="cursor-pointer"
            onClick={() => load_integrations(false)}
          >
            <IconRefresh />
          </button>
        </h1>

        <div className="overflow-x-auto">
          {integrations?.data && integrations?.data?.length > 0 ? (
            <ETLTable
              columns={columns}
              data={integrations}
              load={load_integrations}
              changePage={changePage}
            />
          ) : (
            <Alert>
              <AlertTitle>Heads up!</AlertTitle>
              <AlertDescription>
                No integrations available! Create your first integration now.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
      <Spinner visible={isLoading} />
    </DefaultLayout>
  );
}
