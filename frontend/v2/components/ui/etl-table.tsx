"use client";

import { useState } from "react";
import Link from "next/link";
import { PaginatedIntegrationConfig } from "../types/integration";
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
  IconCircleX,
  IconInfoOctagon,
  IconLoader,
  IconPlayerPlayFilled,
  IconSkull,
  IconTrash,
} from "@tabler/icons-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./tooltip";
import { Card, CardContent } from "./card";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Checkbox } from "./checkbox";
import Spinner from "../Spinner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";
import {
  kill_integration,
  trigger_integration,
  update_integration,
} from "../utils/api";
import { toast } from "sonner";

interface ETLTableInterface {
  columns: string[];
  data: PaginatedIntegrationConfig;
  load: (cache: boolean) => void;
  changePage: (pg: number) => void;
  onBulkDelete: (ids: string[]) => Promise<void>;
}

const ETLTable: React.FC<ETLTableInterface> = (params) => {
  const { columns, data, load, changePage, onBulkDelete } = params;
  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedRows(data.data.map((item) => item.id));
    } else {
      setSelectedRows([]);
    }
  };

  const handleSelectRow = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedRows([...selectedRows, id]);
    } else {
      setSelectedRows(selectedRows.filter((rowId) => rowId !== id));
    }
  };

  const handleBulkDelete = async () => {
    if (!onBulkDelete) return;

    try {
      setIsDeleting(true);
      await onBulkDelete(selectedRows);
      setSelectedRows([]);
      load(false);
    } catch (error) {
      console.error("Error deleting items:", error);
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };

  const onEditIntegration = async (integration_id, is_enabled) => {
    await update_integration({
      pipeline_id: integration_id,
      fields: {
        is_enabled,
      },
    });

    load(false);
  };

  const triggerIntegration = async (integration_id) => {
    setIsLoading(true);
    await trigger_integration(integration_id);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    load(false);
    setIsLoading(false);
    toast.success("Integration triggered successfully");
  };

  const killIntegration = async (integration_id) => {
    setIsLoading(true);
    await kill_integration(integration_id);
    await new Promise((resolve) => setTimeout(resolve, 3000));
    load(false);
    setIsLoading(false);
    toast.success("Kill signal sent to the integration");
  };

  return (
    <div className="relative shadow-md sm:rounded-lg">
      <div
        className={`flex items-center justify-between p-4 bg-muted/50 border-b transition-all duration-200 ${
          selectedRows.length > 0
            ? "opacity-100 translate-y-0"
            : "opacity-0 -translate-y-full h-0 p-0 overflow-hidden"
        }`}
      >
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium">
            {selectedRows.length} {selectedRows.length === 1 ? "item" : "items"}{" "}
            selected
          </span>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setShowDeleteDialog(true)}
            disabled={isDeleting}
            className="gap-2"
          >
            <IconTrash className="w-4 h-4" />
            Delete Selected
          </Button>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelectedRows([])}
          className="text-muted-foreground hover:text-foreground"
        >
          Clear Selection
        </Button>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="p-4">
              <div className="flex items-center">
                <Checkbox
                  id="checkbox-all-search"
                  checked={selectedRows.length === data.data.length}
                  onCheckedChange={handleSelectAll}
                />
                <label className="sr-only">Select all</label>
              </div>
            </TableHead>
            {columns.map((column, i) => (
              <TableHead key={i} className="px-6 py-3">
                {column}
              </TableHead>
            ))}
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
                  <Checkbox
                    id={`checkbox-${key}`}
                    checked={selectedRows.includes(integration.id)}
                    onCheckedChange={(checked) =>
                      handleSelectRow(integration.id, checked as boolean)
                    }
                  />
                  <label className="sr-only">Select row</label>
                </div>
              </TableCell>
              {/* <TableCell className="px-6 py-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="truncate block max-w-[200px]">
                        <Link href={`/pipelines/${integration.id}`}>
                          {integration.id}
                        </Link>
                      </span>
                    </TooltipTrigger>
                    <TooltipContent className="dark:bg-card dark:text-white">
                      <p>{integration.id}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </TableCell> */}
              <TableCell className="px-6 py-4">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <span className="truncate block max-w-[200px]">
                        <Link href={`/pipelines/${integration.id}`}>
                          {integration.integration_name}
                        </Link>
                      </span>
                    </TooltipTrigger>
                    <TooltipContent className="dark:bg-card dark:text-white">
                      <p>{integration.integration_name}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
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
                {integration.integration_type.replace("_", " ").toUpperCase()}
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Select
                    value={integration.is_enabled ? "true" : "false"}
                    onValueChange={async (value) => {
                      const newValue = value === "true";
                      try {
                        await onEditIntegration(integration.id, newValue);
                      } catch (err) {
                        console.error("Failed to update integration", err);
                      }
                    }}
                  >
                    <SelectTrigger className="w-[140px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">
                        <IconCircleCheckFilled className="fill-green-500 dark:fill-green-400" />{" "}
                        Enabled
                      </SelectItem>
                      <SelectItem value="false">
                        <IconCircleX /> Disabled
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </TableCell>
              <TableCell className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Select
                    value={integration.is_running ? "true" : "false"}
                    onValueChange={async (value) => {
                      const newValue = value === "true";
                      try {
                        await onEditIntegration(integration.id, newValue);
                      } catch (err) {
                        console.error("Failed to update integration", err);
                      }
                    }}
                  >
                    <SelectTrigger className="w-[140px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">
                        <IconCircleCheckFilled className="fill-green-500 dark:fill-green-400" />{" "}
                        Running
                      </SelectItem>
                      <SelectItem value="false">
                        <IconCircleX /> Stopped
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {/* <Badge
                  variant="outline"
                  className="text-muted-foreground px-1.5"
                >
                  {integration.is_running === true ? (
                    <IconCircleCheckFilled className="fill-green-500 dark:fill-green-400" />
                  ) : (
                    <IconCircleX />
                  )}
                  {integration.is_running ? "Running" : "Stopped"}
                </Badge> */}
              </TableCell>

              <TableCell className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    title="Trigger Pipeline"
                    disabled={integration.is_running || isLoading}
                    onClick={() => {
                      triggerIntegration(integration.id);
                    }}
                  >
                    <IconPlayerPlayFilled className="w-4 h-4 mr-1" />
                    Trigger
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    title="Kill Pipeline"
                    disabled={!integration.is_running || isLoading}
                    onClick={() => {
                      killIntegration(integration.id);
                    }}
                  >
                    <IconSkull className="w-4 h-4 mr-1" />
                    Kill
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete {selectedRows.length} selected
              item(s). This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleBulkDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isDeleting}
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

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
      <Spinner visible={isDeleting} message="Deleting pipelines..." />
    </div>
  );
};

export default ETLTable;
