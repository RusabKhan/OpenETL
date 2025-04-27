"use client";
import { useEffect, useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import {
  base_url,
  delete_connection,
  fetchCreatedConnections,
} from "@/utils/api";
import CardConnections from "@/components/CardConnection";
import Head from "next/head";
import axios from "axios";
import { Connection } from "@/types/connectors";
import Toast from "@/components/common/Toast";
import Spinner from "@/components/common/Spinner";

const Connections = () => {
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState<
    "success" | "error" | "warning" | "info"
  >("success");
  const [databases, setDatabases] = useState([]);
  const [apis, setApis] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const showToast = (
    message: string,
    type: "success" | "error" | "warning" | "info" = "success",
  ) => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };

  const load = async () => {
    try {
      setIsLoading(true);
      let data_res = await fetchCreatedConnections("database");
      let api_res = await fetchCreatedConnections("api");
      data_res = await updateConnections(data_res);
      api_res = await updateConnections(api_res);
      setDatabases(data_res);
      setApis(api_res);
    } catch (err: any) {
      showToast(
        err.message || "Failed to load connections. Please try again.",
        "error",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const updateConnections = async (connections: Connection[]) => {
    try {
      const updatedConnections = await Promise.all(
        connections.map(async (connection) => {
          const response = await axios.get(
            `${base_url}/connector/get_connector_image/${connection.connector_name}/${connection.connection_type}`,
          );
          return { ...connection, logo: response.data }; // Merge response data
        }),
      );
      return updatedConnections;
    } catch (error) {
      console.error("Error updating connections:", error);
    }
  };

  useEffect(() => {
    document.title = "Celery | OpenETL";

    load();
  }, []);

  const onDelete = async (id: number) => {
    try {
      await delete_connection(id);
    } catch (error: any) {
      showToast(
        error.message || "Failed to delete connections. Please try again.",
        "error",
      );
    } finally {
      load();
    }
  };

  return (
    <DefaultLayout>
      <div>
        {/* <Breadcrumb pageName="Connections" /> */}

        <CardConnections
          connections={databases}
          name="Database Connections"
          isLoading={isLoading}
          onDelete={onDelete}
          load={load}
        />
        <CardConnections
          connections={apis}
          name="API Connections"
          isLoading={isLoading}
          onDelete={onDelete}
          load={load}
        />
        <Toast
          message={toastMessage}
          type={toastType}
          visible={toastVisible}
          onClose={() => setToastVisible(false)}
        />

        <Spinner visible={isLoading} message="Loading connections..." />
      </div>
    </DefaultLayout>
  );
};

export default Connections;
