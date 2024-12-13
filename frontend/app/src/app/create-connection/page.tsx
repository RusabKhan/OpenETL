"use client";

import React, { useEffect, useState } from "react";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { CONNECTION_TYPES } from "@/utils/contants";
import {
  fetchInstalledConnectors,
  getConnectorAuthDetails,
  store_connection,
  test_connection,
} from "@/utils/api";
import { capitalizeFirstLetter, isValidAuthParams } from "@/utils/func";
import { Connectors } from "@/types/connectors";
import { ApiAuthParams, DatabaseAuthParams } from "@/types/auth_params";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import { useRouter } from "next/navigation";

const CreateConnection = () => {
  const [connection, setConnection] = useState({
    connection_type: "database",
    connection_name: "",
    connector_name: "postgresql",
    auth_type: "basic",
  });
  const [connectors, setConnectors] = useState<Connectors>({
    database: [],
    api: [],
  });
  const [fields, setFields] = useState<DatabaseAuthParams | ApiAuthParams>();
  const [authType, setAuthType] = useState<string[]>(["basic"]);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    if (name === "connection_type") {
      setConnection((prev) => ({
        ...prev,
        connector_name:
          value === "database" ? connectors.database[0] : connectors.api[0],
        connection_type: value,
      }));
    } else {
      setConnection((prevConnection) => ({
        ...prevConnection,
        [name]: value,
      }));
    }
  };

  const handleFieldsChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;

    setFields((prevData) => ({
      ...(prevData as DatabaseAuthParams | ApiAuthParams),
      [name]: name === "port" ? parseInt(value, 10) : value,
    }));
  };

  // To be updated
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const test = {
      auth_type: connection.auth_type,
      connector_name: connection.connector_name,
      connector_type: connection.connection_type,
      auth_params: fields as DatabaseAuthParams | ApiAuthParams,
    };
    test_connection(test)
      .then(async (res) => {
        if (res === true) {
          const store = {
            connection_name: connection.connection_name,
            connector_name: connection.connector_name,
            connection_type: connection.connection_type,
            auth_type: connection.auth_type,
            connection_credentials: fields as
              | DatabaseAuthParams
              | ApiAuthParams,
          };
          const response = await store_connection(store);
          if (response[0] === true) {
            router.push("/connections");
          } else {
            setError("Can't save the connection! ❌");
          }
        } else {
          setError("Test Connection Failed! ❌");
        }
      })
      .catch((err: any) => {
        console.log(err);
      });
  };

  const getInstalledConnectors = async () => {
    const response = await fetchInstalledConnectors();
    setConnectors(response);
  };

  const getConnectorAuth = async (name: string, type: string) => {
    const response = await getConnectorAuthDetails(name, type);
    const firstKeys = Object.keys(response);
    const values = Object.values(response)[0];
    setFields((prevFields) => {
      if (isValidAuthParams(values)) {
        return values;
      }
      return prevFields;
    });
    setAuthType(firstKeys);
  };

  useEffect(() => {
    getInstalledConnectors();
  }, []);

  useEffect(() => {
    getConnectorAuth(connection.connector_name, connection.connection_type);
  }, [connection.connection_type, connection.connector_name]);

  return (
    <>
      <DefaultLayout>
        <div className="mx-auto max-w-4xl">
          <Breadcrumb pageName="Create Connection" />

          <form
            className="space-y-4 rounded-sm border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-boxdark"
            onSubmit={handleSubmit}
          >
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {/* Select Connection Type */}
              <div>
                <label
                  htmlFor="connection_type"
                  className="mb-1 block text-sm font-medium"
                >
                  Select Connection Type
                </label>
                <select
                  name="connection_type"
                  id="connection_type"
                  value={connection.connection_type}
                  onChange={handleChange}
                  className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
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
                  htmlFor="connection_name"
                  className="mb-1 block text-sm font-medium"
                >
                  Connection Name
                </label>
                <input
                  type="text"
                  id="connection_name"
                  name="connection_name"
                  value={connection.connection_name}
                  onChange={handleChange}
                  placeholder="my_connection"
                  className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              {/* Dynamic Fields for Database Connection */}
              <>
                <div>
                  <label
                    htmlFor="connector_name"
                    className="mb-1 block text-sm font-medium"
                  >
                    Select {capitalizeFirstLetter(connection.connection_type)}
                  </label>
                  <select
                    name="connector_name"
                    id="connector_name"
                    value={connection.connector_name}
                    onChange={handleChange}
                    className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="----">----</option>
                    {connection.connection_type === "database"
                      ? connectors.database.map((database, i) => (
                          <option value={database} key={i}>
                            {capitalizeFirstLetter(database)}
                          </option>
                        ))
                      : connectors.api.map((database, i) => (
                          <option value={database} key={i}>
                            {capitalizeFirstLetter(database)}
                          </option>
                        ))}
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="auth_type"
                    className="mb-1 block text-sm font-medium"
                  >
                    Authentication Type
                  </label>
                  <select
                    name="auth_type"
                    id="auth_type"
                    value={connection.auth_type}
                    onChange={handleChange}
                    className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    {authType.map((auth, i) => (
                      <option value={auth} key={i}>
                        {capitalizeFirstLetter(auth)}
                      </option>
                    ))}
                  </select>
                </div>

                {fields && (
                  <>
                    {Object.entries(fields).map(([key, value]) => (
                      <div key={key}>
                        <label
                          style={{ display: "block", marginBottom: "5px" }}
                        >
                          {key.charAt(0).toUpperCase() + key.slice(1)}:
                        </label>
                        <input
                          type={typeof value === "number" ? "number" : "text"}
                          name={key}
                          value={value}
                          onChange={handleFieldsChange}
                          className="w-full rounded-sm bg-whiten p-2 text-black focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                        />
                      </div>
                    ))}
                  </>
                )}
              </>
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
            {error && (
              <div
                className="relative rounded border border-red-400 bg-red-100 px-4 py-3 text-red-700"
                role="alert"
              >
                <strong className="font-bold">Error!</strong>
                <span className="block sm:inline">{error}</span>
              </div>
            )}
          </form>
        </div>
      </DefaultLayout>
    </>
  );
};

export default CreateConnection;
