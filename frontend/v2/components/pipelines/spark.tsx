"use client";

import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { IntegrationConfig } from "../types/integration";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";

interface IntegrationProps {
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}

interface ConfigInterface {
  config: string;
  value: string;
  isEditing: boolean;
}

const SparkConfigTab: React.FC<IntegrationProps> = ({
  integration,
  setIntegration,
}) => {
  const [sparkConfig, setSparkConfig] = useState<ConfigInterface[]>([]);
  const [hadoopConfig, setHadoopConfig] = useState<ConfigInterface[]>([]);

  useEffect(() => {
    const mapConfig = (config: Record<string, string>) =>
      Object.entries(config).map(([key, value]) => ({
        config: key,
        value,
        isEditing: false,
      }));

    setSparkConfig(mapConfig(integration.spark_config));
    setHadoopConfig(mapConfig(integration.hadoop_config));
  }, [integration]);

  const handleAddRow = (
    setConfig: Dispatch<SetStateAction<ConfigInterface[]>>
  ) =>
    setConfig((prev) => [...prev, { config: "", value: "", isEditing: true }]);

  const handleDeleteRow = (
    setConfig: Dispatch<SetStateAction<ConfigInterface[]>>,
    index: number
  ) => setConfig((prev) => prev.filter((_, idx) => idx !== index));

  const handleEditRow = (
    setConfig: Dispatch<SetStateAction<ConfigInterface[]>>,
    index: number
  ) =>
    setConfig((prev) =>
      prev.map((item, idx) =>
        idx === index ? { ...item, isEditing: !item.isEditing } : item
      )
    );

  const handleChangeRow = (
    setConfig: Dispatch<SetStateAction<ConfigInterface[]>>,
    index: number,
    field: "config" | "value",
    value: string
  ) =>
    setConfig((prev) =>
      prev.map((item, idx) =>
        idx === index ? { ...item, [field]: value } : item
      )
    );

  const saveConfig = (
    config: ConfigInterface[],
    key: "spark_config" | "hadoop_config"
  ) => {
    const updatedConfig = config.reduce(
      (acc, { config, value }) => ({ ...acc, [config]: value }),
      {}
    );
    setIntegration((prev) => ({ ...prev, [key]: updatedConfig }));
  };

  const renderTable = (
    data: ConfigInterface[],
    setConfig: Dispatch<SetStateAction<ConfigInterface[]>>,
    key: "spark_config" | "hadoop_config"
  ) => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Key</TableHead>
          <TableHead>Value</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, index) => (
          <TableRow key={`${row.config}-${index}`}>
            <TableCell>
              {row.isEditing ? (
                <Input
                  value={row.config}
                  onChange={(e) =>
                    handleChangeRow(setConfig, index, "config", e.target.value)
                  }
                  placeholder="Key"
                />
              ) : (
                row.config
              )}
            </TableCell>
            <TableCell>
              {row.isEditing ? (
                <Input
                  value={row.value}
                  onChange={(e) =>
                    handleChangeRow(setConfig, index, "value", e.target.value)
                  }
                  placeholder="Value"
                />
              ) : (
                row.value
              )}
            </TableCell>
            <TableCell className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (row.isEditing) saveConfig(data, key);
                  handleEditRow(setConfig, index);
                }}
              >
                {row.isEditing ? "Save" : "Edit"}
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleDeleteRow(setConfig, index)}
              >
                Delete
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  return (
    <div className="space-y-4">
      {/* Spark Configuration */}
      <Card className="py-0 px-4">
        <Accordion type="single" collapsible>
          <AccordionItem value="spark">
            <AccordionTrigger className="w-full">
              <CardHeader className="w-full p-0">
                <CardTitle>Spark Configuration</CardTitle>
              </CardHeader>
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-0">
                <div className="flex justify-between items-center mb-2">
                  <span></span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleAddRow(setSparkConfig)}
                  >
                    Add Row
                  </Button>
                </div>
                {renderTable(sparkConfig, setSparkConfig, "spark_config")}
              </CardContent>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Hadoop Configuration */}
      <Card className="py-0 px-4">
        <Accordion type="single" collapsible>
          <AccordionItem value="hadoop">
            <AccordionTrigger className="w-full">
              <CardHeader className="w-full p-0">
                <CardTitle>Hadoop Configuration</CardTitle>
              </CardHeader>
            </AccordionTrigger>
            <AccordionContent>
              <CardContent>
                <div className="flex justify-between items-center mb-2">
                  <span>Hadoop Configurations</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleAddRow(setHadoopConfig)}
                  >
                    Add Row
                  </Button>
                </div>
                {renderTable(hadoopConfig, setHadoopConfig, "hadoop_config")}
              </CardContent>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>
    </div>
  );
};

export default SparkConfigTab;
