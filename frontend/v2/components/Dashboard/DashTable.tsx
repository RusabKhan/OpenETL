"use client";

import { DashboardConfig } from "../types/integration";
import { formatDateTime, truncateText } from "../utils/func";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { Card, CardContent } from "../ui/card";
import { Car } from "lucide-react";

interface DashTableProps {
  columns: string[];
  data: DashboardConfig;
  changePage: (page: number) => void;
}

export default function DashTable({
  columns,
  data,
  changePage,
}: DashTableProps) {
  return (
    <div className="space-y-4">
      {/* Table */}
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column, i) => (
              <TableHead key={i}>{column}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.integrations.data.map((integration, key) => (
            <TableRow key={key}>
              <TableCell>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="truncate block max-w-[200px]">
                        {integration.integration_name}
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>{integration.integration_name}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </TableCell>
              <TableCell>{integration.run_count}</TableCell>
              <TableCell>
                <Badge
                  variant={
                    integration.latest_run_status === "success"
                      ? "outline"
                      : integration.latest_run_status === "running"
                      ? "secondary"
                      : "destructive"
                  }
                >
                  {integration.latest_run_status}
                </Badge>
              </TableCell>
              <TableCell>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="truncate block max-w-[200px]">
                        {truncateText(integration.error_message)}
                      </span>
                    </TooltipTrigger>
                    {integration.error_message && (
                      <TooltipContent className="m-0 p-0">
                        <Card className="max-w-[600px] max-h-[400px] overflow-y-auto whitespace-pre-wrap break-words rounded-none">
                          <CardContent>
                            <p className="text-sm text-muted-foreground">
                              {integration.error_message}
                            </p>
                          </CardContent>
                        </Card>
                      </TooltipContent>
                    )}
                  </Tooltip>
                </TooltipProvider>
              </TableCell>
              <TableCell>{formatDateTime(integration.start_date)}</TableCell>
              <TableCell>{formatDateTime(integration.end_date)}</TableCell>
            </TableRow>
          ))}
          {data.integrations.data.length === 0 && (
            <TableRow>
              <TableCell colSpan={columns.length} className="text-center">
                No data available
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      {/* Pagination */}
      <nav
        className="flex flex-wrap items-center justify-between pt-4"
        aria-label="Table navigation"
      >
        <div className="text-sm text-muted-foreground">
          Total Pages:{" "}
          <span className="font-semibold text-foreground">
            {data.total_pages}
          </span>
          , Total Items:{" "}
          <span className="font-semibold text-foreground">
            {data.total_items}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {data.page !== 1 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => changePage(data.page - 1)}
            >
              Previous
            </Button>
          )}
          <Button variant="outline" size="sm" disabled>
            {data.page}
          </Button>
          {data.total_pages !== data.page && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => changePage(data.page + 1)}
            >
              Next
            </Button>
          )}
        </div>
      </nav>
    </div>
  );
}
