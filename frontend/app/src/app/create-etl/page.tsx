"use client";

import React, { Dispatch, SetStateAction, useEffect, useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import {
  capitalizeFirstLetter,
  getCurrentDate,
  getCurrentTime,
} from "@/utils/func";
import { IntegrationConfig } from "@/types/integration";
import { fetch_metadata, fetchCreatedConnections } from "@/utils/api";
import { StoreConnections } from "@/types/store_connections";
import { Metadata, ParamMetadata } from "@/types/connectors";
import Spinner from "@/components/common/Spinner";

interface IntegrationProps {
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}

const tabs = ["Select Source & Target", "Spark/Hadoop Config", "Finish"];
const source_types = ["database", "api"];
const target_types = ["database"];

const initial_integration: IntegrationConfig = {
  frequency: "Weekly",
  hadoop_config: {},
  integration_name: "",
  integration_type: "full_load",
  schedule_date: [getCurrentDate()],
  schedule_time: getCurrentTime(),
  source_connection: 1,
  source_schema: "public",
  source_table: "",
  spark_config: {
    "spark.app.name": "",
    "spark.driver.memory": "1g",
    "spark.executor.cores": "1",
    "spark.executor.instances": "1",
    "spark.executor.memory": "1g",
  },
  target_connection: 1,
  target_schema: "public",
  target_table: "",
};

const CreateEtl = () => {
  const [activeTab, setActiveTab] = useState("selectsource&target");
  const [integration, setIntegration] =
    useState<IntegrationConfig>(initial_integration);

  const handleNextTab = () => {
    if (activeTab === "selectsource&target") {
      setActiveTab("spark/hadoopconfig");
    } else if (activeTab === "spark/hadoopconfig") {
      setActiveTab("finish");
    }
  };

  const handlePreviousTab = () => {
    if (activeTab === "spark/hadoopconfig") {
      setActiveTab("selectsource&target");
    } else if (activeTab === "finish") {
      setActiveTab("spark/hadoopconfig");
    }
  };
  return (
    <DefaultLayout>
      <div className="mx-auto max-w-7xl p-6">
        <Breadcrumb pageName="Create ETL" />

        {/* Tabs */}
        <div className="mb-6 flex gap-4 border-b border-gray-300">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === tab.toLowerCase().replace(/ /g, "")
                  ? "border-b-2 border-blue-500 text-blue-500"
                  : "text-gray-600"
              }`}
              onClick={() => setActiveTab(tab.toLowerCase().replace(/ /g, ""))}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "selectsource&target" && (
          <SourceTargetTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}
        {activeTab === "spark/hadoopconfig" && <SparkConfigTab />}
        {activeTab === "finish" && <FinishTab />}

        {/* Navigation buttons */}
        <div className="mt-6 flex justify-between">
          {activeTab !== "selectsource&target" && (
            <button
              onClick={handlePreviousTab}
              className="rounded bg-gray-300 px-4 py-2 text-gray-700"
            >
              Previous
            </button>
          )}
          {activeTab !== "finish" && (
            <button
              onClick={handleNextTab}
              className="rounded bg-blue-500 px-4 py-2 text-white"
            >
              Next
            </button>
          )}
          {activeTab === "finish" && (
            <button
              onClick={() => alert("ETL Integration Created!")}
              className="rounded bg-green-500 px-4 py-2 text-white"
            >
              Create Integration
            </button>
          )}
        </div>
      </div>
    </DefaultLayout>
  );
};

// Source & Target Tab
const SourceTargetTab: React.FC<IntegrationProps> = (
  integration,
  setIntegration,
) => {
  const [sourceType, setSourceType] = useState("database");
  const [targetType, setTargetType] = useState("database");
  const [sourceConnections, setSourceConnections] = useState<
    StoreConnections[]
  >([]);
  const [targetConnections, setTargetConnections] = useState<
    StoreConnections[]
  >([]);
  const [metadata, setMetadata] = useState<Metadata | undefined>();
  const [sourceSchema, setSourceSchema] = useState("");
  const [sourceTable, setSourceTable] = useState("");
  const [targetSchema, setTargetSchema] = useState("");
  const [targetTable, setTargetTable] = useState("");
  const [sourceIsLoading, setSourceIsLoading] = useState(false);
  const [targetIsLoading, setTargetIsLoading] = useState(false);

  const getConnections = async (source: string, isSource: boolean) => {
    try {
      const res = await fetchCreatedConnections(source);
      if (isSource) {
        setSourceConnections(res);
      } else {
        setTargetConnections(res);
      }
    } catch (error: any) {
      console.error(error);
    }
  };

  const getMetadata = async (param: ParamMetadata) => {
    setSourceIsLoading(true);
    try {
      const res = await fetch_metadata(param);
      setMetadata(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setSourceIsLoading(false);
    }
  };

  useEffect(() => {
    getConnections(sourceType);
  }, []);

  const handleSourceTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setSourceIsLoading(true);
    const source = event.target.value;
    setSourceType(source);
    getConnections(source, true);
    setSourceIsLoading(false);
  };

  const handleTargetTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setTargetIsLoading(true);
    const target = event.target.value;
    setTargetType(target);
    getConnections(target, false);
    setTargetIsLoading(false);
  };

  const handleConnectionChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
    connections: StoreConnections[],
  ) => {
    const { value } = event.target;
    if (value !== "-") {
      const selected =
        connections.find((source) => source.connection_name === value) ||
        connections[0];

      const metadata = {
        auth_options: {
          auth_type: {
            name: selected.auth_type.toUpperCase(),
            value: selected.auth_type,
          },
          connection_credentials: selected.connection_credentials,
          connection_name: selected.connection_name,
          connection_type: selected.connection_type,
          connector_name: selected.connector_name,
        },
        connector_name: selected.connector_name,
        connector_type: selected.connection_type,
      };

      getMetadata(metadata);
    }
  };

  return (
    <div className="space-y-6">
      {/* Source Section */}
      <div className="rounded-sm border bg-white p-6 dark:bg-boxdark">
        <h2 className="mb-4 text-lg font-semibold">Source</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Source</label>
            <select
              onChange={(e) => handleConnectionChange(e, sourceConnections)}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {sourceConnections.map((source: StoreConnections, i) => (
                <option value={source.connection_name} key={i}>
                  {source.connection_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">
              Source Type
            </label>
            <div className="flex items-center gap-4">
              {source_types.map((type, i) => (
                <label className="flex items-center" key={i}>
                  <input
                    type="radio"
                    name="sourceType"
                    value={type}
                    checked={sourceType === type}
                    className="mr-2"
                    onChange={handleSourceTypeChange}
                  />
                  {capitalizeFirstLetter(type)}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Source Schema
            </label>
            <select
              value={sourceSchema}
              onChange={(e) => setSourceSchema(e.target.value)}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {metadata &&
                Object.keys(metadata).map((schema, i) => (
                  <option value={schema} key={i}>
                    {schema}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Source Tables
            </label>
            <select
              value={sourceTable}
              onChange={(e) => setSourceTable(e.target.value)}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {metadata !== undefined && sourceSchema && (
                <>
                  {Array.isArray(metadata[sourceSchema])
                    ? metadata[sourceSchema].map((table, i) => (
                        <option value={table} key={i}>
                          {table}
                        </option>
                      ))
                    : Object.keys(metadata[sourceSchema]).map((table, i) => (
                        <option value={table} key={i}>
                          {table}
                        </option>
                      ))}
                </>
              )}
            </select>
          </div>
          {sourceIsLoading && <Spinner />}
        </div>
      </div>

      {/* Target Section */}
      <div className="rounded-sm border bg-white p-6 dark:bg-boxdark">
        <h2 className="mb-4 text-lg font-semibold">Target</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Target</label>
            <select
              onChange={(e) => handleConnectionChange(e, sourceConnections)}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {sourceConnections.map((target: StoreConnections, i) => (
                <option value={target.connection_name} key={i}>
                  {target.connection_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Type
            </label>
            <div className="flex items-center gap-4">
              {target_types.map((type, i) => (
                <label className="flex items-center" key={i}>
                  <input
                    type="radio"
                    name="targetType"
                    value={type}
                    checked={targetType === type}
                    className="mr-2"
                    onChange={handleTargetTypeChange}
                  />
                  {capitalizeFirstLetter(type)}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Schema
            </label>
            <input
              type="text"
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              value="public"
              readOnly
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Tables
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="targetTable"
                  value="database"
                  defaultChecked
                  className="mr-2"
                />
                New
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="targetTable"
                  value="database"
                  className="mr-2"
                />
                Existing
              </label>
            </div>
          </div>
          <div></div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Tables
            </label>
            <select className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
              <option value="-">----</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};

// Spark/Hadoop Config Tab
const SparkConfigTab = () => {
  const [sparkConfig, setSparkConfig] = useState([
    { config: "spark.driver.memory", value: "1g", isEditing: false },
    { config: "spark.executor.memory", value: "1g", isEditing: false },
    { config: "spark.executor.cores", value: "1", isEditing: false },
    { config: "spark.executor.instances", value: "1", isEditing: false },
    {
      config: "spark.app.name",
      value: "my_connection_to_my_connection",
      isEditing: false,
    },
  ]);

  const [hadoopConfig, setHadoopConfig] = useState([]);

  // Add a new row to the table
  const handleAddRow = (setConfig: any) => {
    setConfig((prev: any) => [
      ...prev,
      { config: "new.config.key", value: "new_value", isEditing: true },
    ]);
  };

  // Delete a row from the table
  const handleDeleteRow = (setConfig: any, index: any) => {
    setConfig((prev: any) => prev.filter((_: any, idx: any) => idx !== index));
  };

  const handleEdit = (setConfig: any, index: any) => {
    setConfig((prev: any) =>
      prev.map((item: any, idx: any) =>
        idx === index ? { ...item, isEditing: !item.isEditing } : item,
      ),
    );
  };

  const handleChange = (setConfig: any, index: any, newValue: any) => {
    setConfig((prev: any) =>
      prev.map((item: any, idx: any) =>
        idx === index ? { ...item, value: newValue } : item,
      ),
    );
  };

  const renderTable = (data: any, setConfig: any) => (
    <>
      {data ? (
        <table className="w-full border-collapse border border-gray-300 bg-white dark:bg-boxdark">
          <thead>
            <tr>
              <th className="border border-gray-300 px-4 py-2">
                Configuration
              </th>
              <th className="border border-gray-300 px-4 py-2">Value</th>
              <th className="border border-gray-300 px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row: any, index: any) => (
              <tr key={`${row.config}-${index}`}>
                <td className="border border-gray-300 px-4 py-2">
                  {row.isEditing ? (
                    <input
                      type="text"
                      value={row.config}
                      onChange={(e) =>
                        setConfig((prev: any) =>
                          prev.map((item: any, idx: any) =>
                            idx === index
                              ? { ...item, config: e.target.value }
                              : item,
                          ),
                        )
                      }
                      className="w-full border border-gray-300 px-2 py-1"
                    />
                  ) : (
                    row.config
                  )}
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  {row.isEditing ? (
                    <input
                      type="text"
                      value={row.value}
                      onChange={(e) =>
                        handleChange(setConfig, index, e.target.value)
                      }
                      className="w-full border border-gray-300 px-2 py-1"
                    />
                  ) : (
                    row.value
                  )}
                </td>
                <td className="flex items-center justify-center gap-2 border border-gray-300 px-4 py-2 text-center">
                  <button
                    onClick={() => handleEdit(setConfig, index)}
                    className="flex items-center text-blue-500 hover:text-blue-700"
                  >
                    {row.isEditing ? (
                      // Check icon
                      <svg
                        className="h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    ) : (
                      // Pencil icon
                      <svg
                        className="h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M17.121 2.879a3 3 0 00-4.242 0L5 9.244V12h2.756l8.879-8.879a3 3 0 000-4.242zM3 14v3h3l8.879-8.879a3 3 0 000-4.242l-1.5-1.5a3 3 0 00-4.242 0L3 10.756V14z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </button>
                  <button
                    onClick={() => handleDeleteRow(setConfig, index)}
                    className="flex items-center text-red-500 hover:text-red-700"
                  >
                    {/* Trash icon */}
                    <svg
                      className="h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M19 7l-1 14H6L5 7m5 4v6m4-6v6m1-9V5a1 1 0 00-1-1h-4a1 1 0 00-1 1v1m-4 0h14"
                      />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <span>No data found!</span>
      )}
    </>
  );

  return (
    <div>
      <div className="grid grid-cols-2 gap-8">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-md font-semibold">Spark Configuration</h3>
            <button
              onClick={() => handleAddRow(setSparkConfig)}
              className="flex items-center text-green-500 hover:text-green-700"
            >
              {/* Add icon */}
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
          {renderTable(sparkConfig, setSparkConfig)}
        </div>
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-md font-semibold">Hadoop Configuration</h3>
            <button
              onClick={() => handleAddRow(setHadoopConfig)}
              className="flex items-center text-green-500 hover:text-green-700"
            >
              {/* Add icon */}
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
          {renderTable(hadoopConfig, setHadoopConfig)}
        </div>
      </div>
    </div>
  );
};

// Finish Tab
const FinishTab = () => (
  <div className="space-y-6">
    <div className="rounded-sm border bg-white p-6 dark:bg-boxdark">
      <h2 className="mb-4 text-lg font-semibold">Finish</h2>
      <div className="grid gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">
            Enter unique integration name
          </label>
          <input
            type="text"
            className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter integration name"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="mb-2">
              <label className="mb-1 block text-sm font-medium">
                Select Schedule Type
              </label>
              <div className="flex flex-col gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="scheduleType"
                    value="frequency"
                    defaultChecked
                    className="mr-2"
                  />
                  Frequency
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="scheduleType"
                    value="selectedDates"
                    className="mr-2"
                  />
                  Selected Dates
                </label>
              </div>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">
                Select Frequency
              </label>
              <select className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white">
                <option value="weekly">Weekly</option>
              </select>
            </div>
          </div>
          <div>
            <div className="mb-4">
              <label className="mb-1 block text-sm font-medium">
                Schedule Time
              </label>
              <input
                type="time"
                className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                defaultValue="19:05"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Schedule Date
              </label>
              <input
                type="date"
                className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">
            Select Integration Type
          </label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="integrationType"
                value="fullLoad"
                defaultChecked
                className="mr-2"
              />
              Full Load
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default CreateEtl;
