"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import LogPanel from "@/components/LogPanel";
import { LogsConfig, LogsParam } from "@/components/types/integration";
import { getIntegrations, getPipelineLogs } from "@/components/utils/api";
import { capitalizeFirstLetter } from "@/components/utils/func";
import { useEffect, useState } from "react";

const log_tabs = ["scheduler", "celery", "api"];

const Logs = () => {
  const [activeTab, setActiveTab] = useState("scheduler");
  const [integrations, setIntegrations] = useState();

  const loadIntegrations = async () => {
    const res = await getIntegrations(true, 1);
    setIntegrations(res.data);
  };
  
  useEffect(() => {
    document.title = "Logs | OpenETL";

    loadIntegrations();
  }, []);

  return (
    <DefaultLayout title="Logs">
      <div className="p-4 md:p-6">
        {/* Tabs */}
        <div className="mb-6 flex gap-4 border-b border-border">
          {log_tabs.map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === tab.toLowerCase().replace(/ /g, "")
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground"
              } hover:text-primary`}
              onClick={() => setActiveTab(tab.toLowerCase().replace(/ /g, ""))}
            >
              {capitalizeFirstLetter(tab)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-background rounded-md shadow">
          {activeTab === "scheduler" && <SchedulerLogs />}
          {activeTab === "celery" && <CeleryLogs />}
          {activeTab === "api" && <ApiLogs integrations={integrations} />}
        </div>
      </div>
    </DefaultLayout>
  );
};

const SchedulerLogs = () => {
  const [logsData, setLogsData] = useState<LogsConfig>();
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const loadLogs = async (cache: boolean) => {
    setIsloading(true);
    const params = {
      logs_type: "scheduler",
      per_page: 20,
      page: page,
    };
    const res = await getPipelineLogs(cache, params);
    setLogsData(res.data);
    setIsloading(false);
  };

  const nextPage = () => {
    setPage(page + 1);
  };

  const previousPage = () => {
    setPage(page - 1);
  };

  useEffect(() => {
    loadLogs(true);
  }, [page]);

  return (
    <LogPanel
      title="Scheduler Logs"
      logsData={logsData}
      isLoading={isLoading}
      nextPage={nextPage}
      previousPage={previousPage}
      reload={loadLogs}
    />
  );
};

const CeleryLogs = () => {
  const [logs, setLogs] = useState<LogsConfig>();
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const nextPage = () => {
    setPage(page + 1);
  };

  const previousPage = () => {
    setPage(page - 1);
  };

  const loadLogs = async (cache: boolean) => {
    setIsloading(true);
    const params = {
      logs_type: "celery",
      per_page: 20,
      page: page,
    };
    const res = await getPipelineLogs(cache, params);
    setLogs(res.data);
    setIsloading(false);
  };

  useEffect(() => {
    loadLogs(true);
  }, [page]);

  return (
    <LogPanel
      title="Celery Logs"
      logsData={logs}
      isLoading={isLoading}
      nextPage={nextPage}
      previousPage={previousPage}
      reload={loadLogs}
    />
  );
};

const ApiLogs = (params: any) => {
  const { integrations } = params;
  const [logs, setLogs] = useState<LogsConfig>();
  const [integration, setIntegration] = useState("-");
  const [isLoading, setIsloading] = useState(false);
  const [page, setPage] = useState(1);

  const nextPage = () => {
    setPage(page + 1);
  };

  const previousPage = () => {
    setPage(page - 1);
  };

  useEffect(() => {
    document.title = "Logs | OpenETL";
  }, []);

  const loadLogs = async (cache: boolean) => {
    setIsloading(true);
    const params: LogsParam = {
      logs_type: "api",
      per_page: 20,
      page: page,
    };
    if (integration !== "-") {
      params["integration_id"] = integration;
    }
    const res = await getPipelineLogs(cache, params);
    setLogs(res.data);
    setIsloading(false);
  };

  useEffect(() => {
    loadLogs(true);
  }, [integration, page]);

  return (
    <div className="space-y-6">
      <h2 className="mb-4 text-lg font-semibold text-foreground">
        Select Integration
      </h2>
      <div>
        <label
          htmlFor="integration"
          className="block text-sm font-medium text-foreground pb-2"
        >
          Integration Name
        </label>
        <select
          name="integration"
          id="integration"
          value={integration}
          onChange={(e) => setIntegration(e.target.value)}
          className="w-full rounded-md border border-input bg-background p-2 text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background"
        >
          <option value="-">----</option>
          {integrations?.data.map((pipeline: any) => (
            <option key={pipeline.id} value={pipeline.id}>
              {pipeline.integration_name}
            </option>
          ))}
        </select>
      </div>
      <LogPanel
        title="Integration Logs"
        logsData={logs}
        isLoading={isLoading}
        nextPage={nextPage}
        previousPage={previousPage}
        reload={loadLogs}
      />
    </div>
  );
};

export default Logs;
