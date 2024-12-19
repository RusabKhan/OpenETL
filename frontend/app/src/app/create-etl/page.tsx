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
import {
  create_integration,
  fetch_metadata,
  fetchCreatedConnections,
} from "@/utils/api";
import {
  GetCreatedConnections,
  Metadata,
  ParamMetadata,
  StoreConnectionsParam,
} from "@/types/connectors";
import Spinner from "@/components/common/Spinner";
import SelectableDates from "@/components/SelectableDates";
import Toast from "@/components/common/Toast";
import { useRouter } from "next/navigation";

interface IntegrationProps {
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}

interface ConfigInterface {
  config: string;
  value: string;
  isEditing: boolean;
}

const tabs = ["Select Source & Target", "Spark/Hadoop Config", "Finish"];
const source_types = ["database", "api"];
const target_types = ["database"];
const target_table_types = ["new", "existing"];
const frequency_options = ["Weekly", "Monthly", "Daily", "Weekends", "Weekday"];

const initial_integration: IntegrationConfig = {
  frequency: "Weekly",
  hadoop_config: {},
  integration_name: "",
  integration_type: "full_load",
  schedule_date: [getCurrentDate()],
  schedule_time: getCurrentTime(),
  source_connection: 0,
  source_schema: "",
  source_table: "",
  spark_config: {
    "spark.app.name": "",
    "spark.driver.memory": "1g",
    "spark.executor.cores": "1",
    "spark.executor.instances": "1",
    "spark.executor.memory": "1g",
  },
  target_connection: 0,
  target_schema: "",
  target_table: "",
  batch_size: 100000,
};

const CreateEtl = () => {
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<
    "success" | "error" | "warning" | "info"
  >("success");

  const [activeTab, setActiveTab] = useState("selectsource&target");
  const [integration, setIntegration] =
    useState<IntegrationConfig>(initial_integration);
  const router = useRouter();

  const showToast = (
    message: string,
    type: "success" | "error" | "warning" | "info" = "success",
  ) => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };

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

  const handleCreateIntegration = () => {
    const create_etl = async () => {
      await create_integration(integration);
      showToast("Creating Integration!... ✅", "success");
      router.push("/integrations");
    };

    create_etl();
  };

  return (
    <DefaultLayout>
      <div>
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
        {activeTab === "spark/hadoopconfig" && (
          <SparkConfigTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}
        {activeTab === "finish" && (
          <FinishTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}

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
              onClick={handleCreateIntegration}
              className="rounded bg-green-500 px-4 py-2 text-white"
            >
              Create Integration
            </button>
          )}
        </div>
        <Toast
          message={toastMessage}
          type={toastType}
          visible={toastVisible}
          onClose={() => setToastVisible(false)}
        />
      </div>
    </DefaultLayout>
  );
};

// Source & Target Tab
const SourceTargetTab: React.FC<IntegrationProps> = (params) => {
  const { integration, setIntegration } = params;
  const [sourceType, setSourceType] = useState("database");
  const [targetType, setTargetType] = useState("database");
  const [targetTableType, setTargetTableType] = useState("new");
  const [sourceConnections, setSourceConnections] = useState<
    GetCreatedConnections[]
  >([]);
  const [targetConnections, setTargetConnections] = useState<
    GetCreatedConnections[]
  >([]);
  const [sourceMetadata, setSourceMetadata] = useState<Metadata | undefined>();
  const [targetMetadata, setTargetMetadata] = useState<Metadata | undefined>();
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

  const getMetadata = async (param: ParamMetadata, is_source: boolean) => {
    if (is_source) {
      setSourceIsLoading(true);
      try {
        const res = await fetch_metadata(param);
        setSourceMetadata(res);
      } catch (err: any) {
        console.error(err);
      } finally {
        setSourceIsLoading(false);
      }
    } else {
      setTargetIsLoading(true);
      try {
        const res = await fetch_metadata(param);
        setTargetMetadata(res);
      } catch (err: any) {
        console.error(err);
      } finally {
        setTargetIsLoading(false);
      }
    }
  };

  useEffect(() => {
    getConnections(sourceType, true);
    getConnections(sourceType, false);
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

  const handleTargetTableTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setTargetIsLoading(true);
    const source = event.target.value;
    setTargetTableType(source);
    setTargetIsLoading(false);
  };

  const handleConnectionChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
    connections: GetCreatedConnections[],
    is_source: boolean,
  ) => {
    const { value } = event.target;
    if (value !== "-") {
      const selected =
        connections.find((source) => source.id === parseInt(value)) ||
        connections[0];

      if (is_source) {
        setIntegration((prev) => ({
          ...prev,
          source_connection: selected.id,
        }));
      } else {
        setIntegration((prev) => ({
          ...prev,
          target_connection: selected.id,
        }));
      }

      const metadata_params = {
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

      getMetadata(metadata_params, is_source);
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
              value={integration.source_connection}
              onChange={(e) =>
                handleConnectionChange(e, sourceConnections, true)
              }
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {sourceConnections.map((source: GetCreatedConnections, i) => (
                <option value={source.id} key={i}>
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
              onChange={(e) => {
                setSourceSchema(e.target.value);
                setIntegration((prev) => ({
                  ...prev,
                  source_schema: e.target.value,
                }));
              }}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {sourceMetadata &&
                Object.keys(sourceMetadata).map((schema, i) => (
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
              onChange={(e) => {
                setSourceTable(e.target.value);
                setIntegration((prev) => ({
                  ...prev,
                  source_table: e.target.value,
                }));
              }}
              disabled={sourceIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {sourceMetadata !== undefined && sourceSchema && (
                <>
                  {Array.isArray(sourceMetadata[sourceSchema])
                    ? sourceMetadata[sourceSchema].map((table, i) => (
                        <option value={table} key={i}>
                          {table}
                        </option>
                      ))
                    : Object.keys(sourceMetadata[sourceSchema]).map(
                        (table, i) => (
                          <option value={table} key={i}>
                            {table}
                          </option>
                        ),
                      )}
                </>
              )}
            </select>
          </div>
          <Spinner visible={sourceIsLoading} message="Loading source..." />
        </div>
      </div>

      {/* Target Section */}
      <div className="rounded-sm border bg-white p-6 dark:bg-boxdark">
        <h2 className="mb-4 text-lg font-semibold">Target</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Target</label>
            <select
              value={integration.target_connection}
              onChange={(e) =>
                handleConnectionChange(e, targetConnections, false)
              }
              disabled={targetIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {targetConnections.map((target: GetCreatedConnections, i) => (
                <option value={target.id} key={i}>
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
            <select
              value={targetSchema}
              onChange={(e) => {
                setTargetSchema(e.target.value);
                setIntegration((prev) => ({
                  ...prev,
                  target_schema: e.target.value,
                }));
              }}
              disabled={targetIsLoading}
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="-">----</option>
              {targetMetadata &&
                Object.keys(targetMetadata).map((schema, i) => (
                  <option value={schema} key={i}>
                    {schema}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Tables
            </label>
            <div className="flex items-center gap-4">
              {target_table_types.map((type, i) => (
                <label className="flex items-center" key={i}>
                  <input
                    type="radio"
                    name="targetTable"
                    value={type}
                    checked={targetTableType === type}
                    className="mr-2"
                    onChange={handleTargetTableTypeChange}
                  />
                  {capitalizeFirstLetter(type)}
                </label>
              ))}
            </div>
          </div>
          <div></div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              Target Tables
            </label>
            {targetTableType === "existing" ? (
              <select
                value={targetTable}
                onChange={(e) => {
                  setTargetTable(e.target.value);
                  setIntegration((prev) => ({
                    ...prev,
                    target_table: e.target.value,
                  }));
                }}
                disabled={targetIsLoading}
                className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="-">----</option>
                {targetMetadata !== undefined && targetSchema && (
                  <>
                    {Array.isArray(targetMetadata[targetSchema])
                      ? targetMetadata[targetSchema].map((table, i) => (
                          <option value={table} key={i}>
                            {table}
                          </option>
                        ))
                      : Object.keys(targetMetadata[targetSchema]).map(
                          (table, i) => (
                            <option value={table} key={i}>
                              {table}
                            </option>
                          ),
                        )}
                  </>
                )}
              </select>
            ) : (
              <input
                type="text"
                value={integration.target_table}
                onChange={(e) =>
                  setIntegration((prev) => ({
                    ...prev,
                    target_table: e.target.value,
                  }))
                }
                className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            )}
          </div>
          <Spinner visible={targetIsLoading} message="Loading target..." />
        </div>
      </div>
    </div>
  );
};

// Spark/Hadoop Config Tab
const SparkConfigTab: React.FC<IntegrationProps> = (params) => {
  const { integration, setIntegration } = params;
  const [sparkConfig, setSparkConfig] = useState<ConfigInterface[]>([]);

  const [hadoopConfig, setHadoopConfig] = useState<ConfigInterface[]>([]);

  useEffect(() => {
    const sparkConfigArray = Object.entries(integration.spark_config).map(
      ([key, value]) => ({
        config: key,
        value: value,
        isEditing: false,
      }),
    );
    const hadoopConfigArray = Object.entries(integration.hadoop_config).map(
      ([key, value]) => ({
        config: key,
        value: value,
        isEditing: false,
      }),
    );
    setSparkConfig(sparkConfigArray);
    setHadoopConfig(hadoopConfigArray);
  }, []);

  const save_spark_config = () => {
    const data = sparkConfig.map((record) => ({
      [record.config]: record.value,
    }));
    const result = data.reduce((acc, current) => {
      const [key, value] = Object.entries(current)[0]; // Extract key-value pair
      acc[key] = value; // Assign to the accumulator
      return acc;
    }, {});
    setIntegration((prev) => ({
      ...prev,
      spark_config: result,
    }));
  };

  const save_hadoop_config = () => {
    const data = hadoopConfig.map((record) => ({
      [record.config]: record.value,
    }));
    const result = data.reduce((acc, current) => {
      const [key, value] = Object.entries(current)[0]; // Extract key-value pair
      acc[key] = value; // Assign to the accumulator
      return acc;
    }, {});
    setIntegration((prev) => ({
      ...prev,
      hadoop_config: result,
    }));
  };

  useEffect(() => {
    // Saves the spark config in integration whenever the table has any changes.
    save_spark_config();
  }, [sparkConfig]);

  useEffect(() => {
    // Saves the hadoop config in integration whenever the table has any changes.
    save_hadoop_config();
  }, [hadoopConfig]);

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
      prev.map((item: any, idx: any) => {
        return idx === index ? { ...item, isEditing: !item.isEditing } : item;
      }),
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
                      onChange={(e) => {
                        setConfig((prev: any) =>
                          prev.map((item: any, idx: any) =>
                            idx === index
                              ? { ...item, config: e.target.value }
                              : item,
                          ),
                        );
                      }}
                      className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
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
                      className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
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
const FinishTab: React.FC<IntegrationProps> = (params) => {
  const { integration, setIntegration } = params;

  const [scheduleType, setScheduleType] = useState("frequency");

  useEffect(() => {
    setIntegration((prev) => ({
      ...prev,
      integration_name: `${integration.source_schema}_${integration.source_table}_to_${integration.target_schema}_${integration.target_table}`,
    }));
  }, []);

  return (
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
              value={integration.integration_name}
              onChange={(e) =>
                setIntegration((prev) => ({
                  ...prev,
                  integration_name: e.target.value,
                }))
              }
              className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Enter integration name"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="mb-4">
                <label className="mb-1 block text-sm font-medium">
                  Select Schedule Type
                </label>
                <div className="flex flex-col gap-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="scheduleType"
                      value="frequency"
                      checked={scheduleType === "frequency"}
                      onChange={(e) => setScheduleType(e.target.value)}
                      className="mr-2"
                    />
                    Frequency
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="scheduleType"
                      value="selectedDates"
                      checked={scheduleType === "selectedDates"}
                      onChange={(e) => setScheduleType(e.target.value)}
                      className="mr-2"
                    />
                    Selected Dates
                  </label>
                </div>
              </div>
              <div className="mb-4">
                <label className="mb-1 block text-sm font-medium">
                  Select Frequency
                </label>
                <select
                  value={integration.frequency}
                  onChange={(e) =>
                    setIntegration((prev) => ({
                      ...prev,
                      frequency: e.target.value,
                    }))
                  }
                  disabled={scheduleType === "selectedDates"}
                  className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  {frequency_options.map((option, i) => (
                    <option value={option} key={i}>
                      {option}
                    </option>
                  ))}
                </select>
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
                      value={integration.integration_type}
                      defaultChecked
                      className="mr-2"
                    />
                    {capitalizeFirstLetter(
                      integration.integration_type.replace("_", " "),
                    )}
                  </label>
                </div>
              </div>
            </div>
            <div>
              <div className="mb-4">
                <label className="mb-1 block text-sm font-medium">
                  Schedule Time
                </label>
                <input
                  type="time"
                  value={integration.schedule_time}
                  onChange={(e) =>
                    setIntegration((prev) => ({
                      ...prev,
                      schedule_time: e.target.value,
                    }))
                  }
                  className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <SelectableDates
                  integration={integration}
                  setIntegration={setIntegration}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium">
                  Batch Size
                </label>
                <input
                  type="number"
                  value={integration.batch_size}
                  onChange={(e) =>
                    setIntegration((prev) => ({
                      ...prev,
                      batch_size: parseInt(e.target.value),
                    }))
                  }
                  className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateEtl;
