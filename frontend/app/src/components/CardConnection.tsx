"use client";

import { Connection } from "@/types/connection";
import React, { useState } from "react";

interface DatabaseConnectionListProps {
  connections: Connection[];
  name: string;
  isLoading: boolean;
}

const CardConnections: React.FC<DatabaseConnectionListProps> = ({
  connections,
  name,
  isLoading,
}) => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-4 text-2xl font-bold">{name}</h1>
      {isLoading ? (
        <div
          className="h-16 w-16 animate-spin rounded-full border-t-4 border-solid border-blue-500"
          role="status"
        ></div>
      ) : (
        <>
          {connections.length === 0 ? (
            <p className="text-gray-500">No connections available.</p>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {connections.map((connection) => (
                <div
                  key={connection.id}
                  className="rounded-lg border bg-white p-4 shadow-md transition-shadow hover:shadow-lg"
                >
                  <img
                    src={connection.logo}
                    alt="Connector logo"
                    width="50"
                    height="50"
                  />
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
        </>
      )}
    </div>
  );
};

export default CardConnections;
