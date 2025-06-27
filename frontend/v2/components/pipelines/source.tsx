"use client";

import { Dispatch, SetStateAction, useEffect, useState } from "react";
import {
  GetCreatedConnections,
  MetadataConfig,
  ParamMetadata,
} from "../types/connectors";
import { IntegrationConfig } from "../types/integration";
import { fetch_metadata, fetchCreatedConnections } from "../utils/api";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { capitalizeFirstLetter } from "../utils/func";
import Spinner from "../Spinner";
import { toast } from "sonner";

interface IntegrationProps {
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}

const source_types = ["database", "api"];
const target_types = ["database"];
const target_table_types = ["new", "existing"];

const SourceTargetTab: React.FC<IntegrationProps> = ({
  integration,
  setIntegration,
}) => {
  const [sourceType, setSourceType] = useState("");
  const [targetType, setTargetType] = useState("");
  const [targetTableType, setTargetTableType] = useState("new");
  const [sourceConnections, setSourceConnections] = useState<
    GetCreatedConnections[]
  >([]);
  const [targetConnections, setTargetConnections] = useState<
    GetCreatedConnections[]
  >([]);
  const [sourceMetadata, setSourceMetadata] = useState<
    MetadataConfig | undefined
  >();
  const [targetMetadata, setTargetMetadata] = useState<
    MetadataConfig | undefined
  >();
  const [sourceSchema, setSourceSchema] = useState("");
  const [sourceTable, setSourceTable] = useState("");
  const [targetSchema, setTargetSchema] = useState("");
  const [targetTable, setTargetTable] = useState("");
  const [sourceIsLoading, setSourceIsLoading] = useState(false);
  const [targetIsLoading, setTargetIsLoading] = useState(false);

  const getMetadata = async (param: ParamMetadata, isSource: boolean) => {
    if (isSource) {
      setSourceIsLoading(true);
      try {
        const res = await fetch_metadata(param);
        setSourceMetadata(res.data);
      } catch (err: any) {
        console.error(err);
      } finally {
        setSourceIsLoading(false);
      }
    } else {
      setTargetIsLoading(true);
      try {
        const res = await fetch_metadata(param);
        setTargetMetadata(res.data);
      } catch (err: any) {
        console.error(err);
      } finally {
        setTargetIsLoading(false);
      }
    }
  };

  const getConnections = async (source: string, isSource: boolean) => {
    try {
      const res = await fetchCreatedConnections(source);
      if (isSource) {
        setSourceConnections(res.data);
      } else {
        setTargetConnections(res.data);
      }
    } catch (error: any) {
      console.error(error);
      toast(error.message || "Failed to get connections!");
    }
  };

  const handleConnectionChange = (
    value: string,
    connections: GetCreatedConnections[],
    is_source: boolean
  ) => {
    if (value !== "-") {
      const selected =
        connections.find((source) => source.id === parseInt(value)) ||
        connections[0];

      if (is_source) {
        setIntegration((prev) => ({
          ...prev,
          source_connection: selected.id,
        }));
      } else {
        setIntegration((prev) => ({
          ...prev,
          target_connection: selected.id,
        }));
      }

      const metadata_params = {
        auth_options: {
          auth_type: {
            name: selected.auth_type.toUpperCase(),
            value: selected.auth_type,
          },
          connection_credentials: selected.connection_credentials,
          connection_name: selected.connection_name,
          connection_type: selected.connection_type,
          connector_name: selected.connector_name,
        },
        connector_name: selected.connector_name,
        connector_type: selected.connection_type,
      };

      getMetadata(metadata_params, is_source);
    }
  };

  const handleTargetTableTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setTargetIsLoading(true);
    const source = event.target.value;
    setTargetTableType(source);
    setTargetIsLoading(false);
  };

  return (
    <div className="space-y-6">
      {/* Source Section */}
      <Card>
        <CardHeader>
          <CardTitle>Source</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Source Type</Label>
              <Select
                onValueChange={(value) => {
                  setSourceType(value);
                  getConnections(value, true);
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Source Type" />
                </SelectTrigger>
                <SelectContent>
                  {source_types.map((type) => (
                    <SelectItem key={type} value={type}>
                      {capitalizeFirstLetter(type)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Source Connection</Label>
              <Select
                onValueChange={(value) =>
                  handleConnectionChange(value, sourceConnections, true)
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Source Connection" />
                </SelectTrigger>
                <SelectContent>
                  {sourceConnections.map((source) => (
                    <SelectItem key={source.id} value={source.id.toString()}>
                      {source.connection_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Source Schema</Label>
              <Select
                onValueChange={(value) => {
                  setSourceSchema(value);
                  setIntegration((prev) => ({
                    ...prev,
                    source_schema: value,
                  }));
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Source Schema" />
                </SelectTrigger>
                <SelectContent>
                  {sourceMetadata &&
                    Object.keys(sourceMetadata).map((schema) => (
                      <SelectItem key={schema} value={schema}>
                        {schema}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Source Table</Label>
              <Select
                onValueChange={(value) => {
                  setSourceTable(value);
                  setIntegration((prev) => ({
                    ...prev,
                    source_table: value,
                  }));
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Source Table" />
                </SelectTrigger>
                <SelectContent>
                  {sourceMetadata &&
                    sourceSchema &&
                    (Array.isArray(sourceMetadata[sourceSchema])
                      ? sourceMetadata[sourceSchema].map((table) => (
                          <SelectItem key={table} value={table}>
                            {table}
                          </SelectItem>
                        ))
                      : Object.keys(sourceMetadata[sourceSchema]).map(
                          (table) => (
                            <SelectItem key={table} value={table}>
                              {table}
                            </SelectItem>
                          )
                        ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          {sourceIsLoading && <Spinner visible={sourceIsLoading} />}
        </CardContent>
      </Card>

      {/* Target Section */}
      <Card>
        <CardHeader>
          <CardTitle>Target</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Target Type</Label>
              <Select
                onValueChange={(value) => {
                  setTargetType(value);
                  getConnections(value, false);
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Target Type" />
                </SelectTrigger>
                <SelectContent>
                  {target_types.map((type) => (
                    <SelectItem key={type} value={type}>
                      {capitalizeFirstLetter(type)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Target Connection</Label>
              <Select
                onValueChange={(value) =>
                  handleConnectionChange(value, targetConnections, false)
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Target Connection" />
                </SelectTrigger>
                <SelectContent>
                  {targetConnections.map((target) => (
                    <SelectItem key={target.id} value={target.id.toString()}>
                      {target.connection_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Target Schema</Label>
              <Select
                onValueChange={(value) => {
                  setTargetSchema(value);
                  setIntegration((prev) => ({
                    ...prev,
                    target_schema: value,
                  }));
                }}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select Target Schema" />
                </SelectTrigger>
                <SelectContent>
                  {targetMetadata &&
                    Object.keys(targetMetadata).map((schema) => (
                      <SelectItem key={schema} value={schema}>
                        {schema}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Target Tables
              </label>
              <div className="flex items-center gap-4">
                {target_table_types.map((type, i) => (
                  <label className="flex items-center" key={i}>
                    <input
                      type="radio"
                      name="targetTable"
                      value={type}
                      checked={targetTableType === type}
                      className="mr-2"
                      onChange={handleTargetTableTypeChange}
                    />
                    {capitalizeFirstLetter(type)}
                  </label>
                ))}
              </div>
            </div>
            <div></div>
            <div>
              <Label>Target Table</Label>
              {targetTableType === "existing" ? (
                <Select
                  onValueChange={(value) => {
                    setTargetTable(value);
                    setIntegration((prev) => ({
                      ...prev,
                      target_table: value,
                    }));
                  }}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select Target Table" />
                  </SelectTrigger>
                  <SelectContent>
                    {targetMetadata &&
                      targetSchema &&
                      (Array.isArray(targetMetadata[targetSchema])
                        ? targetMetadata[targetSchema].map((table) => (
                            <SelectItem key={table} value={table}>
                              {table}
                            </SelectItem>
                          ))
                        : Object.keys(targetMetadata[targetSchema]).map(
                            (table) => (
                              <SelectItem key={table} value={table}>
                                {table}
                              </SelectItem>
                            )
                          ))}
                  </SelectContent>
                </Select>
              ) : (
                <Input
                  value={integration.target_table}
                  onChange={(e) =>
                    setIntegration((prev) => ({
                      ...prev,
                      target_table: e.target.value,
                    }))
                  }
                  placeholder="Enter Target Table"
                />
              )}
            </div>
          </div>
          {targetIsLoading && <Spinner visible={targetIsLoading} />}
        </CardContent>
      </Card>
    </div>
  );
};

export default SourceTargetTab;
