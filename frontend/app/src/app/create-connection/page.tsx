"use client";

import React, { useEffect, useState } from "react";
import Head from "next/head";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { CONNECTION_TYPES } from "@/utils/contants";
import { fetchInstalledConnectors } from "@/utils/api";

const CreateConnection = () => {
  const [connection, setConnection] = useState({
    connectionType: "database",
    authType: "basic",
    username: "",
    password: "",
    hostname: "",
    port: 0,
    database: "",
    connectionName: "",
    databaseType: "postgresql",
    apiType: "hubspot",
    token: "",
  });
  const [databaseConnector, setDatabaseConnectors] = useState([]);
  const [apiConnector, setApiConnectors] = useState([]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setConnection((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Connection Data:", connection);
  };

  const getInstalledConnectors = async () => {
    const response = await fetchInstalledConnectors();
    setDatabaseConnectors(response.database);
    setApiConnectors(response.api);
  };

  useEffect(() => {
    getInstalledConnectors();
  }, []);

  return (
    <>
      <Head>
        <title>Create Connection | OpenETL</title>
        <meta
          name="description"
          content="Create Conection page for OpenETL dashboard"
        />
      </Head>
      <DefaultLayout>
        <div className="mx-auto max-w-4xl">
          <h1 className="mb-6 text-2xl font-bold">Create Connection</h1>
          <form
            className="space-y-4 rounded-lg bg-gray-800 p-6 shadow-md"
            onSubmit={handleSubmit}
          >
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {/* Select Connection Type */}
              <div>
                <label
                  htmlFor="connectionType"
                  className="mb-1 block text-sm font-medium"
                >
                  Select Connection Type
                </label>
                <select
                  name="connectionType"
                  id="connectionType"
                  value={connection.connectionType}
                  onChange={handleChange}
                  className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {CONNECTION_TYPES.map((type, i) => (
                    <option value={type.value} key={i}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Connection Name */}
              <div>
                <label
                  htmlFor="connectionName"
                  className="mb-1 block text-sm font-medium"
                >
                  Connection Name
                </label>
                <input
                  type="text"
                  id="connectionName"
                  name="connectionName"
                  value={connection.connectionName}
                  onChange={handleChange}
                  placeholder="my_connection"
                  className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              {/* Dynamic Fields for Database Connection */}
              {connection.connectionType === "database" && (
                <>
                  <div>
                    <label
                      htmlFor="databaseType"
                      className="mb-1 block text-sm font-medium"
                    >
                      Select Database
                    </label>
                    <select
                      name="databaseType"
                      id="databaseType"
                      value={connection.databaseType}
                      onChange={handleChange}
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {databaseConnector.map((database, i) => (
                        <option value={database} key={i}>
                          {database}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="authType"
                      className="mb-1 block text-sm font-medium"
                    >
                      Authentication Type
                    </label>
                    <select
                      name="authType"
                      id="authType"
                      value={connection.authType}
                      onChange={handleChange}
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="basic">Basic</option>
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="username"
                      className="mb-1 block text-sm font-medium"
                    >
                      Username
                    </label>
                    <input
                      type="text"
                      id="username"
                      name="username"
                      value={connection.username}
                      onChange={handleChange}
                      placeholder="Enter username"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="password"
                      className="mb-1 block text-sm font-medium"
                    >
                      Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      name="password"
                      value={connection.password}
                      onChange={handleChange}
                      placeholder="Enter password"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="hostname"
                      className="mb-1 block text-sm font-medium"
                    >
                      Hostname
                    </label>
                    <input
                      type="text"
                      id="hostname"
                      name="hostname"
                      value={connection.hostname}
                      onChange={handleChange}
                      placeholder="localhost"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="port"
                      className="mb-1 block text-sm font-medium"
                    >
                      Port
                    </label>
                    <input
                      type="number"
                      id="port"
                      name="port"
                      value={connection.port}
                      onChange={handleChange}
                      placeholder="5432"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="col-span-2">
                    <label
                      htmlFor="database"
                      className="mb-1 block text-sm font-medium"
                    >
                      Database
                    </label>
                    <input
                      type="text"
                      id="database"
                      name="database"
                      value={connection.database}
                      onChange={handleChange}
                      placeholder="openetl"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </>
              )}

              {/* Dynamic Fields for API Connection */}
              {connection.connectionType === "api" && (
                <>
                  <div>
                    <label
                      htmlFor="apiType"
                      className="mb-1 block text-sm font-medium"
                    >
                      Select API
                    </label>
                    <select
                      name="apiType"
                      id="apiType"
                      value={connection.apiType}
                      onChange={handleChange}
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {apiConnector.map((api, i) => (
                        <option value={api} key={i}>
                          {api}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="authType"
                      className="mb-1 block text-sm font-medium"
                    >
                      Authentication Type
                    </label>
                    <select
                      name="authType"
                      id="authType"
                      value={connection.authType}
                      onChange={handleChange}
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="bearer">Bearer</option>
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label
                      htmlFor="token"
                      className="mb-1 block text-sm font-medium"
                    >
                      Token
                    </label>
                    <input
                      type="text"
                      id="token"
                      name="token"
                      value={connection.token}
                      onChange={handleChange}
                      placeholder="Enter API token"
                      className="w-full rounded-md bg-gray-700 p-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </>
              )}
            </div>

            {/* Submit Button */}
            <div className="text-right">
              <button
                type="submit"
                className="rounded-md bg-blue-500 px-4 py-2 font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Create Connection
              </button>
            </div>
          </form>
        </div>
      </DefaultLayout>
    </>
  );
};

export default CreateConnection;
