"use client";

import { useEffect, useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import ETLTable from "@/components/Tables/ETLTable";
import { PaginatedIntegrationConfig } from "@/types/integration";
import { getIntegrations } from "@/utils/api";
import Spinner from "@/components/common/Spinner";

const initial_list = {
  page: 1,
  per_page: 10,
  total_items: 1,
  total_pages: 1,
  data: [],
};

const Integrations = () => {
  const [integrations, setIntegrations] =
    useState<PaginatedIntegrationConfig>(initial_list);
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const load_integrations = async () => {
    setIsloading(true);
    const response = await getIntegrations(page);
    setIntegrations(response);
    setIsloading(false);
  };

  const changePage = (pg: number) => {
    setPage(pg);
  };

  useEffect(() => {
    load_integrations();
  }, [page]);

  const columns = [
    "Id",
    "Name",
    "Type",
    "Cron Expression",
    "Explanation",
    "Is Enabled",
    "Is Running",
  ];

  return (
    <>
      <DefaultLayout>
        <Breadcrumb pageName="List Integrations" />
        {integrations?.data && integrations?.data?.length > 0 ? (
          <ETLTable
            columns={columns}
            data={integrations}
            load={load_integrations}
            changePage={changePage}
          />
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

export default Integrations;
