import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { capitalizeFirstLetter, isValidAuthParams } from "../utils/func";
import { ApiAuthParams, DatabaseAuthParams } from "../types/auth_params";
import { CONNECTION_TYPES } from "../utils/contants";
import {
  fetchInstalledConnectors,
  getConnectorAuthDetails,
  store_connection,
  test_connection,
} from "../utils/api";
import { useRouter } from "next/navigation";
import { Connectors } from "../types/connectors";

interface CreateProps {
  closeForm: () => void;
  load: () => void;
}

// Reusable FormField Component
const FormField = ({
  label,
  name,
  value,
  onChange,
  options,
  type = "text",
  placeholder,
}: {
  label: string;
  name: string;
  value: string | number;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  options?: { value: string; label: string }[];
  type?: string;
  placeholder?: string;
}) => (
  <div className="space-y-2">
    <label htmlFor={name} className="block text-sm font-medium text-foreground">
      {label}
    </label>
    {options ? (
      <select
        name={name}
        id={name}
        value={value}
        onChange={onChange}
        className="block w-full rounded-md border border-input bg-background p-2 text-sm text-foreground shadow-sm focus:border-primary focus:ring-primary"
      >
        {options.map((option, i) => (
          <option value={option.value} key={i}>
            {option.label}
          </option>
        ))}
      </select>
    ) : (
      <input
        type={type}
        name={name}
        id={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="block w-full rounded-md border border-input bg-background p-2 text-sm text-foreground shadow-sm focus:border-primary focus:ring-primary"
        required
      />
    )}
  </div>
);

// Reusable DynamicFields Component
const DynamicFields = ({
  fields,
  onChange,
}: {
  fields: DatabaseAuthParams | ApiAuthParams | undefined;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
}) => (
  <>
    {fields &&
      Object.entries(fields).map(([key, value]) => (
        <FormField
          key={key}
          label={capitalizeFirstLetter(key)}
          name={key}
          value={value}
          onChange={onChange}
          type={
            key === "password"
              ? "password"
              : typeof value === "number"
              ? "number"
              : "text"
          }
        />
      ))}
  </>
);

const CreateConnection: React.FC<CreateProps> = ({ closeForm, load }) => {
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
  const [authType, setAuthType] = useState<string[]>([]);

  const router = useRouter();

  // Fetch connectors on mount
  useEffect(() => {
    document.title = "Create Connection | OpenETL";

    const fetchConnectors = async () => {
      const response = await fetchInstalledConnectors();
      setConnectors(response.data);
    };

    fetchConnectors();
  }, []);

  // Fetch auth details when connection type or connector changes
  useEffect(() => {
    const fetchAuthDetails = async () => {
      const response = await getConnectorAuthDetails(
        connection.connector_name,
        connection.connection_type
      );

      const values = Object.values(response.data)[0];

      if (isValidAuthParams(values)) {
        setFields(values);
      }

      setAuthType(Object.keys(response.data));
    };

    fetchAuthDetails();
  }, [connection.connection_type, connection.connector_name]);

  // Derived state for connector options
  const connectorOptions = useMemo(() => {
    return connection.connection_type === "database"
      ? connectors.database.map((db) => ({
          value: db,
          label: capitalizeFirstLetter(db),
        }))
      : connectors.api.map((api) => ({
          value: api,
          label: capitalizeFirstLetter(api),
        }));
  }, [connection.connection_type, connectors]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;

      setConnection((prev) => {
        if (name === "connection_type") {
          return {
            ...prev,
            auth_type: value === "database" ? "basic" : "bearer",
            connection_type: value,
            connector_name:
              value === "database" ? connectors.database[0] : connectors.api[0],
          };
        }

        return { ...prev, [name]: value };
      });
    },
    [connectors]
  );

  const handleFieldsChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;

      setFields((prevFields) => ({
        ...(prevFields as DatabaseAuthParams | ApiAuthParams),
        [name]: name === "port" ? parseInt(value, 10) : value,
      }));
    },
    []
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      const testPayload = {
        auth_type: connection.auth_type,
        connector_name: connection.connector_name,
        connector_type: connection.connection_type,
        auth_params: fields as DatabaseAuthParams | ApiAuthParams,
      };

      if (!isValidAuthParams(fields)) {
        toast.error("Invalid authentication parameters! ❌");
        return;
      }

      if (connection.connection_name.length < 3) {
        toast.error("Connection name must be at least 3 characters!");
        return;
      }
      if (connection.connection_name.length > 20) {
        toast.error("Connection name must be at most 20 characters!");
        return;
      }
      if (connection.connection_name.includes(" ")) {
        toast.error("Connection name must not contain spaces!");
        return;
      }

      try {
        const testResult = await test_connection(testPayload);
        if (!testResult.data) {
          toast.error("Test Connection Failed!");
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
        
        if (response.data[0]) {
          toast.success("Connection added!");
          closeForm();
          load();
        } else {
          toast.error("Can't save the connection!");
        }
      } catch (error: any) {
        toast.error(error || "Can't save the connection!");
      }
    },
    [connection, fields, router]
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-background rounded-lg shadow-lg p-6 w-full max-w-xl">
        <h2 className="text-lg font-bold mb-4 text-foreground">
          Create Connection
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <FormField
              label="Select Connection Type"
              name="connection_type"
              value={connection.connection_type}
              onChange={handleChange}
              options={CONNECTION_TYPES.map((type) => ({
                value: type.value,
                label: type.label,
              }))}
            />
            <FormField
              label="Connection Name"
              name="connection_name"
              value={connection.connection_name}
              onChange={handleChange}
              placeholder="my_connection"
            />
            <FormField
              label={`Select ${capitalizeFirstLetter(
                connection.connection_type
              )}`}
              name="connector_name"
              value={connection.connector_name}
              onChange={handleChange}
              options={connectorOptions}
            />
            <FormField
              label="Authentication Type"
              name="auth_type"
              value={connection.auth_type}
              onChange={handleChange}
              options={authType.map((auth) => ({
                value: auth,
                label: capitalizeFirstLetter(auth),
              }))}
            />
            <DynamicFields fields={fields} onChange={handleFieldsChange} />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-foreground bg-secondary hover:bg-secondary/80 focus-visible:ring focus-visible:ring-ring focus-visible:ring-offset-2"
              onClick={closeForm}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white dark:text-black bg-primary hover:bg-primary/80 focus-visible:ring focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateConnection;
