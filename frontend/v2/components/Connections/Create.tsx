import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { capitalizeFirstLetter, isValidAuthParams } from "../utils/func";
import { ApiAuthParams, DatabaseAuthParams } from "../types/auth_params";
import {
  fetchInstalledConnectors,
  getConnectorAuthDetails,
  store_connection,
  test_connection,
} from "../utils/api";
import { useRouter } from "next/navigation";
import { Connectors } from "../types/connectors";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Input } from "../ui/input";

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
  onChange: (value: string) => void;
  options?: { value: string; label: string }[];
  type?: string;
  placeholder?: string;
}) => (
  <div className="space-y-2">
    <Label>{label}</Label>
    {options ? (
      <Select onValueChange={onChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder={`Select ${label}`} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option, i) => (
            <SelectItem key={option.value} value={option.value}>
              {capitalizeFirstLetter(option.label)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    ) : (
      <Input
        type={type}
        name={name}
        id={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
  fields: DatabaseAuthParams | ApiAuthParams | unknown;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
}) => (
  <>
    {fields &&
      Object.entries(fields).map(([key, value]) => (
        <FormField
          key={key}
          label={capitalizeFirstLetter(key).replace(/_/g, " ")}
          name={key}
          value={value}
          onChange={(val: string) => {
            const event = {
              target: {
                name: key,
                value: val,
              },
            } as React.ChangeEvent<HTMLInputElement>;
            onChange(event);
          }}
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
    connection_type: "",
    connection_name: "",
    connector_name: "",
    auth_type: "",
  });
  const [connectors, setConnectors] = useState<Connectors>({});
  const [authType, setAuthType] = useState<string[]>([]);
  const [fields, setFields] = useState<DatabaseAuthParams | ApiAuthParams | unknown>(null);

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
  const fetchAuthDetails = async (connector_name: string, connection_type: string) => {
    const response = await getConnectorAuthDetails(
      connector_name,
      connection_type
    );
    const values = Object.values(response.data)[0];
    setFields(values);

    setAuthType(Object.keys(response.data));
  };

  // Optimized derived state for connector options
  const connectorOptions = useMemo(() => {
    const type = connection.connection_type;
    const options = connectors[type as keyof Connectors] || [];
    return options.map((item) => ({
      value: item,
      label: capitalizeFirstLetter(item),
    }));
  }, [connection.connection_type, connectors]);

  const handleConnectionTypeChange = useCallback(
    (value: string) => {
      setConnection((prev) => ({
        ...prev,
        connection_type: value,
        connector_name: "",
        auth_type: "",
      }));
    },
    []
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;

      setConnection((prev) => {
        if (name == "connector_name") {
          fetchAuthDetails(value, prev.connection_type);
          return {
            ...prev,
            connector_name: value,
            auth_type: "",
          };
        }

        return { ...prev, [name]: value };
      });
    },
    [connectors, authType]
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
        auth_params: fields,
      };

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
        if (!testResult || !testResult.data) {
          toast.error("Test Connection Failed!");
          return;
        }

        const storePayload = {
          connection_name: connection.connection_name,
          connector_name: connection.connector_name,
          connection_type: connection.connection_type,
          auth_type: connection.auth_type,
          connection_credentials: fields,
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
              onChange={handleConnectionTypeChange}
              options={Object.keys(connectors).map((type) => {
                if (connectors[type].length > 0) {
                  return {
                    value: type,
                    label: capitalizeFirstLetter(type),
                  }
                }
              })}
            />
            <FormField
              label="Connection Name"
              name="connection_name"
              value={connection.connection_name}
              onChange={(value: string) =>
                handleChange({
                  target: { name: "connection_name", value },
                } as React.ChangeEvent<HTMLInputElement>)
              }
              placeholder="my_connection"
            />
            <FormField
              label={`Select ${capitalizeFirstLetter(
                connection.connection_type
              )}`}
              name="connector_name"
              value={connection.connector_name}
              onChange={(value: string) =>
                handleChange({
                  target: { name: "connector_name", value },
                } as React.ChangeEvent<HTMLInputElement>)
              }
              options={connectorOptions}
            />
            <FormField
              label="Authentication Type"
              name="auth_type"
              value={connection.auth_type}
              onChange={(value: string) =>
                handleChange({
                  target: { name: "auth_type", value },
                } as React.ChangeEvent<HTMLInputElement>)
              }
              options={authType.map((auth) => ({
                value: auth,
                label: capitalizeFirstLetter(auth),
              }))}
            />
            <DynamicFields fields={fields} onChange={handleFieldsChange} />
          </div>
          <div className="flex justify-end gap-2 mt-2">
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