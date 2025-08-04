"use client";

import ConnectionCards from "@/components/Connections/Cards";
import CreateConnection from "@/components/Connections/Create";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { Connection } from "@/components/types/connectors";
import {
  delete_connection,
  fetchCreatedConnections,
  fetchInstalledConnectors,
  getConnectorImage,
} from "@/components/utils/api";
import { capitalizeFirstLetter } from "@/components/utils/func";
import { PlusIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function Connections() {
  const [connectors, setConnectors] = useState<{ [key: string]: Connection[] }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const load = async () => {
    try {
      setIsLoading(true);
      const installed_connectors = await fetchInstalledConnectors();
      const list_connectors = Object.keys(installed_connectors.data);

      const connectorPromises = list_connectors.map(async (connector) => {
        const response = await fetchCreatedConnections(connector);
        const updatedConnections = await updateConnections(response.data);
        return [connector, updatedConnections] as [string, Connection[]];
      });

      const connectorEntries = await Promise.all(connectorPromises);
      const connectorsObj = Object.fromEntries(connectorEntries);
      setConnectors(connectorsObj);

    } catch (err: any) {
      if (!err.message.includes("undefined"))
        toast.error(
          err.message || "Failed to load connections. Please try again."
        );
    } finally {
      setIsLoading(false);
    }
  };

  const updateConnections = async (connections: Connection[]) => {
    try {
      const updatedConnections = await Promise.all(
        connections.map(async (connection) => {
          const response = await getConnectorImage(
            connection.connector_name,
            connection.connection_type
          );
          return { ...connection, logo: response.data }; // Merge response data
        })
      );
      return updatedConnections;
    } catch (error) {
      console.error("Error updating connections:", error);
    }
  };

  useEffect(() => {
    document.title = "Connections | OpenETL";

    load();
  }, []);

  const onDelete = async (id: number) => {
    try {
      await delete_connection(id);
    } catch (error: any) {
      toast.error(
        error.message || "Failed to delete connections. Please try again."
      );
    } finally {
      load();
    }
  };

  return (
    <DefaultLayout title="Connections">
      <div className="flex flex-1 flex-col relative p-4 md:p-6">
        <div className="absolute top-4 right-4 md:top-6 md:right-6 z-10">
          <button
            className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm bg-gray-800 hover:bg-gray-700 dark:bg-gray-200 dark:text-gray-900 dark:hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            onClick={() => setIsDialogOpen(true)}
          >
            <PlusIcon /> Create Connection
          </button>
        </div>
        <div className="@container/main flex flex-1 flex-col gap-2">
          {Object.keys(connectors).map((connector, index) => (
            <div className="flex flex-col gap-2 pb-4" key={index}>
              <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {capitalizeFirstLetter(connector)}
              </h2>
              <ConnectionCards
                connections={connectors[connector] as Connection[]}
                loading={isLoading}
                onDelete={onDelete}
                load={load}
              />
            </div>
          ))}
        </div>

        {isDialogOpen && (
          <CreateConnection
            closeForm={() => {
              setIsDialogOpen(false);
            }}
            load={load}
          />
        )}
      </div>
    </DefaultLayout>
  );
}
