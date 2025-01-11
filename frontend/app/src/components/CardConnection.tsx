"use client";

import React, { useState } from "react";
import Spinner from "./common/Spinner";
import { Connection } from "@/types/connectors";
import EditConnection from "./DynamicForm/EditConnection";

interface DatabaseConnectionListProps {
  connections: Connection[];
  name: string;
  isLoading: boolean;
  onDelete: (id: number) => void;
  load: () => void;
}

const CardConnections: React.FC<DatabaseConnectionListProps> = ({
  connections,
  name,
  isLoading,
  onDelete,
  load,
}) => {
  const [selectedConnection, setSelectedConnection] =
    useState<Connection | null>(null);
  const [deleteConnection, setDeleteConnection] = useState<Connection | null>(
    null,
  );
  const [showForm, setShowForm] = useState(false);

  const handleDelete = (id: number) => {
    setDeleteConnection(null);
    onDelete(id);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-4 text-xl font-bold">{name}</h1>
      {connections.length === 0 ? (
        <p className="text-gray-500">No connections available.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {connections.map((connection) => (
            <div
              key={connection.id}
              className="group relative rounded-lg border bg-white p-6 shadow-lg transition-transform hover:scale-105 hover:shadow-xl dark:bg-boxdark"
            >
              <div className="absolute right-2 top-2 flex space-x-2 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  onClick={() => setSelectedConnection(connection)}
                  className="rounded bg-blue-500 px-3 py-1 text-sm font-medium text-white transition hover:bg-blue-600"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                    className="size-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                    />
                  </svg>
                </button>
                <button
                  onClick={() => setDeleteConnection(connection)}
                  className="rounded bg-red-500 px-3 py-1 text-sm font-medium text-white transition hover:bg-red-600"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                    className="size-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                    />
                  </svg>
                </button>
              </div>
              {/* Card Content */}
              <div className="flex flex-col md:flex-row items-center space-x-2">
                <img
                  src={connection.logo}
                  alt="Connector logo"
                  className="h-12 w-12 object-contain"
                />
                <div>
                  <h2 className="text-lg font-bold text-gray-800 dark:text-white">
                    {connection.connection_name}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-whiten">
                    {connection.connector_name}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {selectedConnection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="relative w-96 rounded-lg bg-white p-6 shadow-lg dark:bg-boxdark">
            {/* Close Button */}
            <button
              onClick={() => setSelectedConnection(null)}
              className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="2"
                stroke="currentColor"
                className="h-6 w-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            <div className="flex items-center space-x-4">
              <img
                src={selectedConnection.logo}
                alt="Connector logo"
                className="h-12 w-12 object-contain"
              />
              <div>
                <div className="flex items-center space-x-4">
                  <h2 className="text-xl font-bold text-gray-800 dark:text-white">
                    {selectedConnection.connection_name}
                  </h2>
                  <button
                    onClick={() => setShowForm(true)}
                    className="ext-gray-400 hover:text-gray-600"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="1.5"
                      stroke="currentColor"
                      className="size-6"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                      />
                    </svg>
                  </button>
                </div>
                <p className="text-sm text-gray-500 dark:text-whiten">
                  {selectedConnection.connector_name} (
                  {selectedConnection.auth_type})
                </p>
              </div>
            </div>

            {/* Dynamic Fields */}
            <form>
              <h4 className="my-2 text-lg font-bold text-gray-800 dark:text-white">
                Credentials
              </h4>
              {Object.entries(selectedConnection.connection_credentials).map(
                ([key, value]) => (
                  <div key={key} className="mb-4">
                    <label
                      htmlFor={key}
                      className="block text-sm font-medium capitalize text-gray-700 dark:text-whiten"
                    >
                      {key.replace("_", " ")} {/* Format label */}
                    </label>
                    <input
                      id={key}
                      name={key}
                      value={value}
                      disabled
                      className="mt-1 w-full rounded border bg-whiten p-2 text-gray-700 shadow-sm focus:border-blue-500 focus:outline-none dark:bg-boxdark dark:text-white"
                    />
                  </div>
                ),
              )}
            </form>
          </div>
          {showForm && (
            <EditConnection
              data={selectedConnection}
              closeForm={() => {
                setShowForm(false);
                setSelectedConnection(null);
                load();
              }}
            />
          )}
        </div>
      )}
      {deleteConnection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-sm rounded-lg border bg-white p-6 shadow-md dark:bg-boxdark">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Confirm Delete
            </h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-white">
              Are you sure you want to delete{" "}
              <strong>{deleteConnection.connection_name}</strong>? This action
              cannot be undone.
            </p>
            <div className="mt-4 flex justify-end space-x-4">
              <button
                onClick={() => setDeleteConnection(null)}
                className="rounded bg-gray-300 px-4 py-2 text-gray-800 hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(parseInt(deleteConnection.id, 10))}
                className="rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
      {/* <Spinner visible={isLoading} message="Loading connection..." /> */}
    </div>
  );
};

export default CardConnections;
