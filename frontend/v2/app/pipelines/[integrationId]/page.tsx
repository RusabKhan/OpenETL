"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { PaginatedIntegrationHistoryConfig } from "@/components/types/integration";
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
import { getIntegrationHistory } from "@/components/utils/api";
import { formatDateTime } from "@/components/utils/func";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import Spinner from "@/components/Spinner";

const IntegrationHistory = () => {
  const { integrationId } = useParams();
  const [data, setData] = useState<PaginatedIntegrationHistoryConfig>();
  const [isLoading, setIsLoading] = useState(false);
  const [page, setPage] = useState(1);

  const load = async () => {
    setIsLoading(true);
    if (!integrationId) {
      console.error("Integration ID is undefined");
      setIsLoading(false);
      return;
    }
    const resp = await getIntegrationHistory(integrationId.toString(), page);
    setData(resp.data);
    setIsLoading(false);
  };

  const changePage = (pg: number) => {
    setPage(pg);
  };

  useEffect(() => {
    document.title = "Integration History | OpenETL";
    load();
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

  return (
    <DefaultLayout title="Pipelines">
      <div className="p-4 md:p-6">
        {/* Breadcrumb */}
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
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Integration Details
              </h2>
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
