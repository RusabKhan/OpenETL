"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { IntegrationConfig, PaginatedIntegrationHistoryConfig } from "@/components/types/integration";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { getIntegrationHistory, update_integration } from "@/components/utils/api";
import { formatDateTime, getCurrentDate, getCurrentTime } from "@/components/utils/func";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import Spinner from "@/components/Spinner";
import { Save, SquarePen, X } from "lucide-react";
import { toast } from "sonner";

const initial_integration: IntegrationConfig = {
  frequency: "Weekly",
  hadoop_config: {},
  integration_name: "",
  integration_type: "full_load",
  schedule_date: [getCurrentDate()],
  schedule_time: getCurrentTime(),
  source_connection: 0,
  source_schema: "",
  source_table: "",
  spark_config: {
    "spark.app.name": "",
    "spark.driver.memory": "1g",
    "spark.executor.cores": "1",
    "spark.executor.instances": "1",
    "spark.executor.memory": "1g",
  },
  target_connection: 0,
  target_schema: "",
  target_table: "",
  batch_size: 100000,
};

const IntegrationHistory = () => {
  const { integrationId } = useParams();
  const [data, setData] = useState<PaginatedIntegrationHistoryConfig>();
  const [integration, setIntegration] =
    useState<IntegrationConfig>(initial_integration);
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [editable, setEditable] = useState(false);

  const load = async (cache: boolean) => {
    setIsLoading(true);
    if (!integrationId) {
      console.error("Integration ID is undefined");
      setIsLoading(false);
      return;
    }
    const resp = await getIntegrationHistory(integrationId.toString(), page, cache);
    setData(resp.data);
    // Set integration data when loading
    if (resp.data?.data) {
      setIntegration({
        frequency: "Weekly", // Default value since not in response
        hadoop_config: resp.data.data.hadoop_config || {},
        integration_name: resp.data.data.integration_name || "",
        integration_type: resp.data.data.integration_type || "full_load",
        schedule_date: [getCurrentDate()],
        schedule_time: getCurrentTime(), // Default since not in response
        source_connection: resp.data.data.source_connection || 0,
        source_schema: resp.data.data.source_schema || "",
        source_table: resp.data.data.source_table || "",
        spark_config: resp.data.data.spark_config || {
          "spark.app.name": "",
          "spark.driver.memory": "1g",
          "spark.executor.cores": "1",
          "spark.executor.instances": "1",
          "spark.executor.memory": "1g",
        },
        target_connection: resp.data.data.target_connection || 0,
        target_schema: resp.data.data.target_schema || "",
        target_table: resp.data.data.target_table || "",
        batch_size: resp.data.data.batch_size || 100000,
      });
    }
    setIsLoading(false);
  };

  const changePage = (pg: number) => {
    setPage(pg);
  };

  useEffect(() => {
    document.title = "Integration History | OpenETL";
    load(true);
  }, [page]);

  const historyColumns = [
    "Id",
    "Integration Id",
    "Run Status",
    "Row Count",
    "Error Message",
    "Start Date",
    "End Date",
    "Created At",
    "Updated At",
  ];

  const handleInputChange = (field: string, value: any) => {
    setIntegration(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleUpdateIntegration = async () => {
    try {
      const updateData = {
        pipeline_id: integrationId as string,
        fields: {
          ...integration
        }
      };
      const res = await update_integration(updateData);
      if (res && 'status' in res && res.status === 204) {
        toast.success("Integration updated successfully!");
        setEditable(false);
        load(false); // Reload data to show updated values
      } else {
        toast.error("Failed to update integration.");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to update integration.");
    }
  };

  const handleCancel = () => {
    setEditable(false);
    // Reload data to reset form to original values
    load(true);
  };

  return (
    <DefaultLayout title="Pipelines">
      <div className="p-4 md:p-6 relative">
        <div className="absolute top-4 right-4 md:top-4 md:right-6 z-10 flex gap-2">
          {editable ? (
            <>
              <button
                className="cursor-pointer inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                onClick={handleUpdateIntegration}
              >
                <Save className="mr-2 h-4 w-4" /> Save Changes
              </button>
              <button
                className="cursor-pointer inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-gray-700 shadow-sm bg-gray-200 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                onClick={handleCancel}
              >
                <X className="mr-2 h-4 w-4" /> Cancel
              </button>
            </>
          ) : (
            <button
              className="cursor-pointer inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm bg-gray-800 hover:bg-gray-700 dark:bg-gray-200 dark:text-gray-900 dark:hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              onClick={() => setEditable(true)}
            >
              <SquarePen className="mr-2 h-4 w-4" /> Edit Pipeline
            </button>
          )}
        </div>
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/">Home</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink href="/pipelines">Pipelines</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Pipeline Detail</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="py-4 md:py-6">
          {/* Integration Details */}
          {data?.data && (
            <div className="mb-8 p-4 border rounded-lg shadow dark:border dark:bg-card">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Integration Details
              </h2>

              {editable ? (
                // Editable Form
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Basic Information */}
                    <div className="space-y-4">
                      <h3 className="text-md font-medium text-gray-900 dark:text-gray-100">Basic Information</h3>

                      <div className="space-y-2">
                        <Label htmlFor="integration_name">Integration Name</Label>
                        <Input
                          id="integration_name"
                          value={integration.integration_name}
                          onChange={(e) => handleInputChange('integration_name', e.target.value)}
                          placeholder="Enter integration name"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="integration_type">Integration Type</Label>
                        <Select
                          value={integration.integration_type}
                          onValueChange={(value) => handleInputChange('integration_type', value)}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select integration type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="full_load">Full Load</SelectItem>
                            <SelectItem value="incremental">Incremental</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="batch_size">Batch Size</Label>
                        <Input
                          id="batch_size"
                          type="number"
                          value={integration.batch_size}
                          onChange={(e) => handleInputChange('batch_size', parseInt(e.target.value) || 0)}
                          placeholder="Enter batch size"
                        />
                      </div>
                    </div>

                    {/* Additional Configuration */}
                    <div className="space-y-4">
                      <h3 className="text-md font-medium text-gray-900 dark:text-gray-100">Additional Configuration</h3>

                      <div className="space-y-2">
                        <Label htmlFor="frequency">Frequency</Label>
                        <Select
                          value={integration.frequency}
                          onValueChange={(value) => handleInputChange('frequency', value)}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select frequency" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Daily">Daily</SelectItem>
                            <SelectItem value="Weekly">Weekly</SelectItem>
                            <SelectItem value="Monthly">Monthly</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="schedule_time">Schedule Time</Label>
                        <Input
                          id="schedule_time"
                          type="time"
                          value={integration.schedule_time}
                          onChange={(e) => handleInputChange('schedule_time', e.target.value)}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="schedule_date">Schedule Date</Label>
                        <Input
                          id="schedule_date"
                          type="date"
                          value={integration.schedule_date[0] || getCurrentDate()}
                          onChange={(e) => handleInputChange('schedule_date', [e.target.value])}
                        />
                      </div>
                    </div>
                  </div>
                </form>
              ) : (
                // Static Display
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      <strong>Name:</strong> {data.data.integration_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Type:</strong> {data.data.integration_type}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Source:</strong> {data.data.source_schema}.
                      {data.data.source_table}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Target:</strong> {data.data.target_schema}.
                      {data.data.target_table}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Last Updated:</strong>{" "}
                      {formatDateTime(data.data.updated_at)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      <strong>Batch Size:</strong> {data.data.batch_size}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Cron Expression:</strong>{" "}
                      {data.data.cron_expression.join(", ")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Is Enabled:</strong>{" "}
                      {data.data.is_enabled ? "Yes" : "No"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      <strong>Is Running:</strong>{" "}
                      {data.data.is_running ? "Yes" : "No"}
                    </p>
                  </div>
                </div>
              )}

              {!editable && (
                <Accordion type="single" collapsible className="mt-4">
                  <AccordionItem value="spark">
                    <AccordionTrigger>Spark Configuration</AccordionTrigger>
                    <AccordionContent>
                      {data.data.spark_config &&
                        Object.keys(data.data.spark_config).length > 0 ? (
                        <div className="p-4 border rounded-lg">
                          {Object.entries(data.data.spark_config).map(
                            ([key, value]) => (
                              <p
                                key={key}
                                className="text-sm text-muted-foreground"
                              >
                                <strong>{key}:</strong> {value}
                              </p>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">
                          No Spark configuration available.
                        </p>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="hadoop">
                    <AccordionTrigger>Hadoop Configuration</AccordionTrigger>
                    <AccordionContent>
                      {data.data.hadoop_config &&
                        Object.keys(data.data.hadoop_config).length > 0 ? (
                        <div className="p-4 border rounded-lg">
                          {Object.entries(data.data.hadoop_config).map(
                            ([key, value]) => (
                              <p
                                key={key}
                                className="text-sm text-muted-foreground"
                              >
                                <strong>{key}:</strong> {value}
                              </p>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">
                          No Hadoop configuration available.
                        </p>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              )}
            </div>
          )}

          {/* History Table */}
          {data?.history && data?.history?.length > 0 ? (
            <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    {historyColumns.map((column, i) => (
                      <TableHead key={i}>{column}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data?.history?.map((integration, key) => (
                    <TableRow key={key}>
                      <TableCell>{integration.id}</TableCell>
                      <TableCell>{integration.integration}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            integration.run_status === "success"
                              ? "outline"
                              : integration.run_status === "running"
                                ? "secondary"
                                : "destructive"
                          }
                        >
                          {integration.run_status}
                        </Badge>
                      </TableCell>
                      <TableCell>{integration.row_count}</TableCell>
                      <TableCell>{integration.error_message}</TableCell>
                      <TableCell>
                        {formatDateTime(integration.start_date)}
                      </TableCell>
                      <TableCell>
                        {formatDateTime(integration.end_date)}
                      </TableCell>
                      <TableCell>
                        {formatDateTime(integration.created_at)}
                      </TableCell>
                      <TableCell>
                        {formatDateTime(integration.updated_at)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <nav
                className="flex items-center justify-between pt-4 md:pt-6"
                aria-label="Table navigation"
              >
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Total Pages:{" "}
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {data.total_pages}
                  </span>
                  , Total Items:{" "}
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {data.total_items}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => changePage(data.page - 1)}
                    disabled={data.page === 1}
                  >
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled>
                    {data.page}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => changePage(data.page + 1)}
                    disabled={data.page === data.total_pages}
                  >
                    Next
                  </Button>
                </div>
              </nav>
            </div>
          ) : (
            <Alert>
              <AlertTitle>Heads up!</AlertTitle>
              <AlertDescription>
                No history records found! Wait for the pipeline to execute.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
      <Spinner visible={isLoading} />
    </DefaultLayout>
  );
};

export default IntegrationHistory;
