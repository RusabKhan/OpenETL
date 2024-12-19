"use client";

import { useEffect, useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import ETLTable from "@/components/Tables/ETLTable";
import { PaginatedIntegrationConfig } from "@/types/integration";
import { getIntegrations } from "@/utils/api";

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
  const load_integrations = async () => {
    const response = await getIntegrations();
    setIntegrations(response);
  };

  useEffect(() => {
    load_integrations();
  }, []);

  const columns = ["Id", "Name", "Type", "Is Enabled", "Is Running"];

  return (
    <>
      <DefaultLayout>
        <Breadcrumb pageName="List Integrations" />
        <ETLTable
          columns={columns}
          data={integrations?.data}
          load={load_integrations}
        />
      </DefaultLayout>
    </>
  );
};

export default Integrations;
