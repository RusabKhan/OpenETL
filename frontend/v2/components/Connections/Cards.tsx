import React, { useState } from "react";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "../ui/badge";
import { Delete, DeleteIcon, Lock, Trash2Icon } from "lucide-react";
import EditConnection from "./EditConnection";
import { Input } from "../ui/input";

interface Database {
  username: string;
  password: string;
  hostname: string;
  port: number;
  database: string;
}

interface API {
  token: string;
}

interface Connection {
  id: string;
  connection_name: string;
  connection_type: string;
  connector_name: string;
  auth_type: string;
  connection_credentials: Database | API | unknown;
  logo?: string;
}

interface CardProps {
  connections: Connection[];
  loading?: boolean;
  onDelete: (id: number) => void;
  load: () => void;
}
const ConnectionCards: React.FC<CardProps> = ({
  connections,
  loading,
  onDelete,
  load,
}) => {
  const [selectedConnection, setSelectedConnection] =
    useState<Connection | null>(null);
  const [deleteConnection, setDeleteConnection] = useState<Connection | null>(
    null
  );
  const [showForm, setShowForm] = useState(false);

  const handleDelete = (id: number) => {
    setSelectedConnection(null);
    setDeleteConnection(null);
    onDelete(id);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500 border-solid"></div>
        <p className="ml-4 text-lg font-medium text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {connections && connections.length > 0 && (
        <>
          {connections.map((connection) => (
            <Card
              className="@container/card text-left w-full cursor-pointer"
              key={connection.id}
              onClick={() => {
                setSelectedConnection(connection);
              }}
            >
              <div className="flex flex-row items-center pl-6 w-full">
                {connection.logo && (
                  <img
                    src={connection.logo}
                    alt="Connector logo"
                    className="h-12 w-12 object-contain"
                  />
                )}
                <CardHeader>
                  <CardDescription className="flex flex-row items-center gap-2">
                    {connection.connector_name}
                    <Badge variant="outline">
                      <Lock />
                      {connection.auth_type}
                    </Badge>
                  </CardDescription>
                  <CardTitle className="text-xl font-semibold tabular-nums">
                    {connection.connection_name}
                  </CardTitle>
                </CardHeader>
              </div>
            </Card>
          ))}
        </>
      )}

      {selectedConnection && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/60">
          <div className="relative w-112 rounded-lg bg-background p-6 shadow-lg">
            {/* Close Button */}
            <button
              onClick={() => setSelectedConnection(null)}
              className="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
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
              {selectedConnection.logo && (
                <img
                  src={selectedConnection.logo}
                  alt="Connector logo"
                  className="h-12 w-12 object-contain"
                />
              )}
              <div>
                <div className="flex items-center space-x-4">
                  <h2 className="text-xl font-bold text-foreground">
                    {selectedConnection.connection_name}
                  </h2>
                  <button
                    onClick={() => setShowForm(true)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="1.5"
                      stroke="currentColor"
                      className="h-6 w-6"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"
                      />
                    </svg>
                  </button>
                  <button
                    onClick={() => setDeleteConnection(selectedConnection)}
                  >
                    <Trash2Icon color="red" />
                  </button>
                </div>
                <p className="text-sm text-muted-foreground">
                  {selectedConnection.connector_name} (
                  {selectedConnection.auth_type})
                </p>
              </div>
            </div>

            {/* Dynamic Fields */}
            <form>
              <h4 className="my-2 text-lg font-bold text-foreground">
                Credentials
              </h4>
              {Object.entries(selectedConnection.connection_credentials).map(
                ([key, value]) => (
                  <div key={key} className="mb-4">
                    <label
                      htmlFor={key}
                      className="block text-sm font-medium capitalize text-foreground"
                    >
                      {key.replace(/_/g, " ")}
                    </label>
                    <Input
                      id={key}
                      name={key}
                      type={key === "password" ? "password" : "text"}
                      value={value}
                      disabled
                      className="mt-1 w-full rounded border bg-input p-2 text-foreground shadow-sm focus:border-primary focus:outline-none"
                    />
                  </div>
                )
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
        <Dialog
          open={!!deleteConnection}
          onOpenChange={() => setDeleteConnection(null)}
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm Delete</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete{" "}
                <strong>{deleteConnection?.connection_name}</strong>? This
                action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            <div className="mt-4 flex justify-end space-x-4">
              <button
                onClick={() => setDeleteConnection(null)}
                className="rounded bg-gray-300 px-4 py-2 text-gray-800 hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  handleDelete(
                    parseInt(deleteConnection?.id.toString() || "0", 10)
                  )
                }
                className="rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default ConnectionCards;
