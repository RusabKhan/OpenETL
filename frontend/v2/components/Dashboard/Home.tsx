"use client";

import { ChartArea } from "@/components/chart-area";
import { SectionCards } from "@/components/section-cards";

import { useEffect, useState } from "react";
import { DashboardConfig } from "../types/integration";
import { toast } from "sonner";
import { fetchDashboardData } from "../utils/api";
import DashTable from "./DashTable";

export default function Home() {
  const [page, setPage] = useState(1);

  const [dashData, setDashData] = useState<DashboardConfig>({
    page: 1,
    per_page: 10,
    total_items: 0,
    total_pages: 1,
    total_api_connections: 0,
    total_db_connections: 0,
    total_pipelines: 0,
    total_rows_migrated: 0,
    integrations: {
      data: [],
    },
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await fetchDashboardData(page);
        setDashData(result.data);
      } catch (err: any) {
        if (!err.message.includes("undefined"))
          toast.error(err.message || "Failed to load data. Please try again.");
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

  const changePage = (pg: number) => {
    setPage(pg);
  };

  return (
    <div className="flex flex-1 flex-col py-6">
      <div className="@container/main flex flex-1 flex-col gap-2">
        <div className="flex flex-col gap-4 md:gap-6">
          <SectionCards data={dashData} />
          {dashData && (
            <div className="px-4 lg:px-6">
              <ChartArea data={dashData.integrations.data} />
            </div>
          )}
          {dashData && dashData.total_pipelines > 0 && (
            <div className="px-4 lg:px-6">
              <DashTable
                columns={columns}
                data={dashData}
                changePage={changePage}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
