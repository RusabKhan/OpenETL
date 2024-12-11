"use client";

import { base_url } from "@/utils/api";
import axios from "axios";
import React, { useEffect } from "react";

interface DatabaseConnection {
  id: string;
  connection_name: string;
  connection_type: string;
  connector_name: string;
}

interface DatabaseConnectionListProps {
  connections: DatabaseConnection[];
  name: string;
}

const CardConnections: React.FC<DatabaseConnectionListProps> = ({
  connections,
  name,
}) => {
  // const loadLogo = async (name: string, type: string) => {
  //   try {
  //     const response = await axios.get(
  //       `${base_url}/connector/get_connector_image/${name}/${type}`,
  //     );
  //     return response.data;
  //   } catch (error: any) {
  //     console.error("Error fetching connector details:", error.message);
  //     throw new Error(
  //       error.response?.data?.message || "Error fetching connector details",
  //     );
  //   }
  // };
  // useEffect(() => {
  //   console.log(loadLogo("postgresql", "database"));
  // }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-4 text-2xl font-bold">{name}</h1>
      {connections.length === 0 ? (
        <p className="text-gray-500">No connections available.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {connections.map((connection) => (
            <div
              key={connection.id}
              className="rounded-lg border bg-white p-4 shadow-md transition-shadow hover:shadow-lg"
            >
              {/* <img
                src={loadLogo(
                  connection.connector_name,
                  connection.connection_type,
                )}
                alt="Connector logo"
                width="50"
                height="50"
              /> */}
              <h2 className="text-xl font-semibold text-gray-800">
                {connection.connection_name}
              </h2>
              <h6 className="mb-2 text-sm font-semibold text-gray-800">{`(Connector: ${connection.connector_name})`}</h6>
              <p className="text-gray-600">
                <strong>Type:</strong> {connection.connection_type}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CardConnections;
