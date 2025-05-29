"use client";

import { useState } from "react";
import Link from "next/link";
import { PaginatedIntegrationConfig } from "../types/integration";
import EditIntegration from "../DynamicForm/EditIntegration";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "./badge";
import {
  IconCircleCheckFilled,
  IconInfoOctagon,
  IconLoader,
} from "@tabler/icons-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./tooltip";
import { Card, CardContent } from "./card";

interface ETLTableInterface {
  columns: string[];
  data: PaginatedIntegrationConfig;
  load: (cache: boolean) => void;
  changePage: (pg: number) => void;
}

const ETLTable: React.FC<ETLTableInterface> = (params) => {
  const { columns, data, load, changePage } = params;
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="relative shadow-md sm:rounded-lg">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="p-4">
              <div className="flex items-center">
                <input
                  id="checkbox-all-search"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600 dark:focus:ring-offset-gray-800"
                />
                <label className="sr-only">checkbox</label>
              </div>
            </TableHead>
            {columns.map((column, i) => (
              <TableHead key={i} className="px-6 py-3">
                {column}
              </TableHead>
            ))}
            <TableHead className="px-6 py-3">Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.data?.map((integration, key) => (
            <TableRow
              key={key}
              className="hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <TableCell className="p-4 break-all">
                <div className="flex items-center">
                  <input
                    id={`checkbox-${key}`}
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600 dark:focus:ring-offset-gray-800"
                  />
                  <label className="sr-only">checkbox</label>
                </div>
              </TableCell>
              <TableCell className="px-6 py-4">
                <Link href={`/pipelines/${integration.id}`}>
                  {integration.id}
                </Link>
              </TableCell>
              <TableCell className="px-6 py-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="truncate block max-w-[300px]">
                        {integration.integration_name}
                      </span>
                    </TooltipTrigger>
                    <TooltipContent className="dark:bg-card dark:text-white">
                      <p>{integration.integration_name}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </TableCell>
              <TableCell className="px-6 py-4">
                {integration.integration_type}
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="flex flex-col">
                  {integration.cron_expression.map((cron, i) => (
                    <TooltipProvider key={i}>
                      <Tooltip>
                        <TooltipTrigger>
                          <span className="flex items-center gap-2">
                            {cron.cron_expression}{" "}
                            <IconInfoOctagon width={20} />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="m-0 p-0">
                          <Card className="w-72 rounded-none">
                            <CardContent>
                              <p className="text-sm text-muted-foreground">
                                {integration.cron_expression[i].explanation}
                              </p>
                              <br />
                              <p className="text-xs text-muted-foreground">
                                Next run:{" "}
                                <strong>
                                  {
                                    integration.cron_expression[i]
                                      .next_execution_full
                                  }
                                </strong>
                              </p>
                            </CardContent>
                          </Card>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  ))}
                </div>
              </TableCell>
              <TableCell className="px-6 py-4">
                <Badge
                  variant="outline"
                  className="text-muted-foreground px-1.5"
                >
                  {integration.is_enabled === true ? (
                    <IconCircleCheckFilled className="fill-green-500 dark:fill-green-400" />
                  ) : (
                    <IconLoader />
                  )}
                  {integration.is_enabled ? "True" : "False"}
                </Badge>
              </TableCell>
              <TableCell className="px-6 py-4">
                <Badge
                  variant="outline"
                  className="text-muted-foreground px-1.5"
                >
                  {integration.is_running === true ? (
                    <IconCircleCheckFilled className="fill-green-500 dark:fill-green-400" />
                  ) : (
                    <IconLoader />
                  )}
                  {integration.is_running ? "Running" : "Stopped"}
                </Badge>
              </TableCell>
              <TableCell className="px-6 py-4">
                <Button
                  variant="link"
                  onClick={() => {
                    setShowForm(true);
                  }}
                >
                  Edit
                </Button>
                {showForm && (
                  <EditIntegration
                    data={integration}
                    refresh={() => {
                      load(false);
                    }}
                    closeForm={() => {
                      setShowForm(false);
                    }}
                  />
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <nav
        className="flex-row flex w-full flex-wrap items-center justify-between pt-4"
        aria-label="Table navigation"
      >
        <span className="block text-center text-sm font-normal text-gray-500 dark:text-gray-400  md:inline md:w-auto">
          Total Pages:{" "}
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.total_pages}
          </span>
        </span>
        <span className="block  text-sm font-normal text-gray-500 dark:text-gray-400  md:inline md:w-auto">
          Total Items:{" "}
          <span className="font-semibold text-gray-900 dark:text-white">
            {data.total_items}
          </span>
        </span>
        <ul className="inline-flex h-8 -space-x-px text-sm rtl:space-x-reverse">
          {data.page !== 1 && (
            <li>
              <Button
                variant="outline"
                size="sm"
                onClick={() => changePage(data.page - 1)}
              >
                Previous
              </Button>
            </li>
          )}
          <li>
            <Button variant="outline" size="sm" disabled>
              {data.page}
            </Button>
          </li>
          {data.total_pages !== data.page && (
            <li>
              <Button
                variant="outline"
                size="sm"
                onClick={() => changePage(data.page + 1)}
              >
                Next
              </Button>
            </li>
          )}
        </ul>
      </nav>
    </div>
  );
};

export default ETLTable;
