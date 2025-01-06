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
import Toast from "@/components/common/Toast";

const CreateConnection = () => {
  const [connection, setConnection] = useState({
    connection_type: "database",
    connection_name: "",
    connector_name: "postgresql",
    auth_type: "",
  });

  const [connectors, setConnectors] = useState<Connectors>({
    database: [],
    api: [],
  });

  const [fields, setFields] = useState<DatabaseAuthParams | ApiAuthParams>();
  const [authType, setAuthType] = useState<string[]>(["basic"]);
  const router = useRouter();
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<
    "success" | "error" | "warning" | "info"
  >("success");

  const showToast = (
    message: string,
    type: "success" | "error" | "warning" | "info" = "success",
  ) => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };

  useEffect(() => {
    const fetchConnectors = async () => {
      const response = await fetchInstalledConnectors();
      setConnectors(response);
    };

    fetchConnectors();
  }, []);

  useEffect(() => {
    const fetchAuthDetails = async () => {
      const response = await getConnectorAuthDetails(
        connection.connector_name,
        connection.connection_type,
      );

      const values = Object.values(response)[0];

      if (isValidAuthParams(values)) {
        setFields(values);
      }

      setAuthType(Object.keys(response));
    };

    fetchAuthDetails();
  }, [connection.connection_type, connection.connector_name]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;

    setConnection((prev) => {
      if (name === "connection_type") {
        return {
          ...prev,
          connection_type: value,
          connector_name:
            value === "database" ? connectors.database[0] : connectors.api[0],
        };
      }

      return { ...prev, [name]: value };
    });
  };

  const handleFieldsChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;

    setFields((prevFields) => ({
      ...(prevFields as DatabaseAuthParams | ApiAuthParams),
      [name]: name === "port" ? parseInt(value, 10) : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const testPayload = {
      auth_type: connection.auth_type,
      connector_name: connection.connector_name,
      connector_type: connection.connection_type,
      auth_params: fields as DatabaseAuthParams | ApiAuthParams,
    };

    try {
      const testResult = await test_connection(testPayload);
      if (!testResult) {
        showToast("Test Connection Failed! ❌", "error");
        return;
      }

      const storePayload = {
        connection_name: connection.connection_name,
        connector_name: connection.connector_name,
        connection_type: connection.connection_type,
        auth_type: connection.auth_type,
        connection_credentials: fields as DatabaseAuthParams | ApiAuthParams,
      };

      const response = await store_connection(storePayload);

      if (response[0]) {
        showToast("Connection added!", "success");
        router.push("/connections");
      } else {
        showToast("Can't save the connection! ❌", "error");
      }
    } catch (error: any) {
      console.error(error);
      showToast(error.message || "Can't save the connection! ❌", "error");
    }
  };

  return (
    <DefaultLayout>
      <div>
        {/* <Breadcrumb pageName="Create Connection" /> */}

        <form
          className="space-y-4 rounded-sm border border-stroke bg-white p-6 shadow-default dark:border-strokedark dark:bg-boxdark"
          onSubmit={handleSubmit}
        >
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
                  : connectors.api.map((api, i) => (
                      <option value={api} key={i}>
                        {capitalizeFirstLetter(api)}
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
                <option value="-">----</option>
                {authType.map((auth, i) => (
                  <option value={auth} key={i}>
                    {capitalizeFirstLetter(auth)}
                  </option>
                ))}
              </select>
            </div>

            {fields &&
              Object.entries(fields).map(([key, value]) => (
                <div key={key}>
                  <label
                    htmlFor={key}
                    className="mb-1 block text-sm font-medium"
                  >
                    {capitalizeFirstLetter(key)}
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
          </div>

          <div className="text-right">
            <button
              type="submit"
              className="rounded-md bg-blue-500 px-4 py-2 font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Create Connection
            </button>
          </div>
        </form>
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

export default CreateConnection;
