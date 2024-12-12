"use client";
import { useEffect, useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { base_url, fetchCreatedConnections } from "@/utils/api";
import CardConnections from "@/components/CardConnection";
import Head from "next/head";
import axios from "axios";
import { Connection } from "@/types/connection";

const Connections = () => {
  const [databases, setDatabases] = useState([]);
  const [apis, setApis] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const load = async () => {
    setIsLoading(true);
    try {
      let data_res = await fetchCreatedConnections("database");
      let api_res = await fetchCreatedConnections("api");
      data_res = await updateConnections(data_res);
      api_res = await updateConnections(api_res);
      setDatabases(data_res);
      setApis(api_res);
    } catch (err: any) {
      console.log(err.message);
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
    load();
  }, []);

  return (
    <>
      <Head>
        <title>Connections | OpenETL</title>
        <meta
          name="description"
          content="Conections page for OpenETL dashboard"
        />
      </Head>
      <DefaultLayout>
        <div className="mx-auto max-w-242.5">
          <Breadcrumb pageName="Connectors" />

          <CardConnections
            connections={databases}
            name="Database Connections"
            isLoading={isLoading}
          />
          <CardConnections
            connections={apis}
            name="API Connections"
            isLoading={isLoading}
          />
        </div>
      </DefaultLayout>
    </>
  );
};

export default Connections;
