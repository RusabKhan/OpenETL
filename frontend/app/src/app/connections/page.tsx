"use client";
import { useEffect, useState } from "react";
import { Metadata } from "next";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { fetchInstalledConnectors } from "@/utils/api";
import CardConnections from "@/components/CardConnection";

const metadata: Metadata = {
  title: "Connectors | OpenETL",
  description: "This is connectors listing page of OpenETL",
};

const Connections = () => {
  const [databases, setDatabases] = useState([]);
  const [apis, setApis] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data_res = await fetchInstalledConnectors("database");
        const api_res = await fetchInstalledConnectors("api");
        setDatabases(data_res);
        setApis(api_res);
      } catch (err: any) {
        console.log(err.message);
      }
    };

    load();
  }, []);

  return (
    <DefaultLayout>
      <div className="mx-auto max-w-242.5">
        <Breadcrumb pageName="Connectors" />

        <CardConnections connections={databases} name="Database Connections" />
        <CardConnections connections={apis} name="API Connections" />
      </div>
    </DefaultLayout>
  );
};

export default Connections;
