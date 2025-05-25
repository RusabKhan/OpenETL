"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { WorkerStatus, WorkerTasks } from "@/components/types/tasks";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionTrigger,
  AccordionItem,
} from "@/components/ui/accordion";
import {
  IconActivityHeartbeat,
  IconCloudComputing,
  IconDatabase,
  IconRefresh,
  IconReservedLine,
  IconTrash,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";
import {
  clear_tasks,
  getCeleryQueueInfo,
  getCeleryTasks,
  getCeleryWorkerStatus,
} from "@/components/utils/api";
import { toast } from "sonner";
import Spinner from "@/components/Spinner";
import { Card, CardContent } from "@/components/ui/card";

const Celery = () => {
  const [tasks, setTasks] = useState<WorkerTasks | null>(null);
  const [workerStatus, setWorkerStatus] = useState<WorkerStatus | null>(null);
  const [queueInfo, setQueueInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadTasks = async (cache: boolean) => {
    try {
      setIsLoading(true);
      const res = await getCeleryTasks(cache);
      setTasks(res.data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const loadWorkerStatus = async (cache: boolean) => {
    try {
      setIsLoading(true);
      const res = await getCeleryWorkerStatus(cache);
      setWorkerStatus(res.data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load worker status");
    } finally {
      setIsLoading(false);
    }
  };

  const loadQueueInfo = async (cache: boolean) => {
    try {
      setIsLoading(true);
      const res = await getCeleryQueueInfo(cache);
      setQueueInfo(res.data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load queue info");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    document.title = "Celery | OpenETL";

    loadTasks(true);
    loadWorkerStatus(true);
    loadQueueInfo(true);
  }, []);

  return (
    <DefaultLayout title="Celery">
      <div className="p-4 md:p-6">
        <Tabs defaultValue="all-tasks" className="w-full">
          <TabsList>
            <TabsTrigger value="all-tasks">All Tasks</TabsTrigger>
            <TabsTrigger value="worker-status">Worker Status</TabsTrigger>
            <TabsTrigger value="queue-info">Queue Info</TabsTrigger>
          </TabsList>

          <Card className="py-4">
            <CardContent>
              {/* All Tasks Tab */}
              <TabsContent value="all-tasks">
                <AllTasks
                  load={loadTasks}
                  isLoading={isLoading}
                  tasks={tasks}
                />
              </TabsContent>

              {/* Worker Status Tab */}
              <TabsContent value="worker-status">
                <CeleryWorkerStatus
                  load={loadWorkerStatus}
                  isLoading={isLoading}
                  workerStatus={workerStatus}
                />
              </TabsContent>

              {/* Queue Info Tab */}
              <TabsContent value="queue-info">
                <CeleryQueue load={loadQueueInfo} queueInfo={queueInfo} />
              </TabsContent>
            </CardContent>
          </Card>
        </Tabs>
      </div>
      <Spinner visible={isLoading} />
    </DefaultLayout>
  );
};

export default Celery;

const AllTasks = ({
  isLoading,
  tasks,
  load,
}: {
  isLoading: boolean;
  tasks: WorkerTasks | null;
  load: (cache: boolean) => void;
}) => {
  const handleClear = async () => {
    try {
      const res = await clear_tasks();
      toast.success(res.data.message);
    } catch (error: any) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <div className="flex justify-between my-4">
        <h1 className="flex items-center gap-4 text-2xl font-bold mb-6">
          All Tasks{" "}
          <button className="cursor-pointer" onClick={() => load(false)}>
            <IconRefresh />
          </button>
        </h1>
        <button
          className="cursor-pointer inline-flex gap-2 items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm bg-red-800 hover:bg-red-700 dark:bg-red-800 dark:text-gray-200 dark:hover:bg-red-900 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          onClick={handleClear}
        >
          <IconTrash /> Clear Tasks
        </button>
      </div>
      {!isLoading && tasks ? (
        <Accordion type="single" collapsible>
          {/* Active Tasks */}
          <AccordionItem value="active">
            <AccordionTrigger>
              <div className="flex items-center">
                <IconActivityHeartbeat className="mr-2" /> Active Tasks
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {Object.values(tasks.active_tasks).every(
                (taskList) => taskList.length === 0
              ) ? (
                <p className="text-sm text-muted-foreground">
                  No active tasks available.
                </p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(tasks.active_tasks, null, 2)}
                </pre>
              )}
            </AccordionContent>
          </AccordionItem>

          {/* Reserved Tasks */}
          <AccordionItem value="reserved">
            <AccordionTrigger>
              <div className="flex items-center">
                <IconDatabase className="mr-2" /> Reserved Tasks
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {Object.values(tasks.reserved_tasks).every(
                (taskList) => taskList.length === 0
              ) ? (
                <p className="text-sm text-muted-foreground">
                  No reserved tasks available.
                </p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(tasks.reserved_tasks, null, 2)}
                </pre>
              )}
            </AccordionContent>
          </AccordionItem>

          {/* Scheduled Tasks */}
          <AccordionItem value="scheduled">
            <AccordionTrigger>
              <div className="flex items-center">
                <IconCloudComputing className="mr-2" /> Scheduled Tasks
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {Object.values(tasks.scheduled_tasks).every(
                (taskList) => taskList.length === 0
              ) ? (
                <p className="text-sm text-muted-foreground">
                  No scheduled tasks available.
                </p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(tasks.scheduled_tasks, null, 2)}
                </pre>
              )}
            </AccordionContent>
          </AccordionItem>

          {/* Registered Tasks */}
          <AccordionItem value="registered">
            <AccordionTrigger>
              <div className="flex items-center">
                <IconReservedLine className="mr-2" /> Registered Tasks
              </div>
            </AccordionTrigger>
            <AccordionContent>
              {Object.values(tasks.registered).every(
                (taskList) => taskList.length === 0
              ) ? (
                <p className="text-sm text-muted-foreground">
                  No registered tasks available.
                </p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(tasks.registered, null, 2)}
                </pre>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : (
        <p className="text-sm text-muted-foreground">
          No tasks data available.
        </p>
      )}
    </>
  );
};

const CeleryWorkerStatus = ({
  isLoading,
  workerStatus,
  load,
}: {
  isLoading: boolean;
  workerStatus: WorkerStatus | null;
  load: (cache: boolean) => void;
}) => {
  return (
    <>
      <div className="flex justify-between my-4">
        <h1 className="flex items-center gap-4 text-2xl font-bold mb-6">
          Worker Status{" "}
          <button className="cursor-pointer" onClick={() => load(false)}>
            <IconRefresh />
          </button>
        </h1>
      </div>
      {!isLoading && workerStatus ? (
        <Accordion type="single" collapsible>
          {workerStatus.active_workers && (
            <AccordionItem value="active">
              <AccordionTrigger>
                <div className="flex items-center">
                  <IconActivityHeartbeat className="mr-2" /> Active Tasks
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(workerStatus.active_workers, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          )}
          {workerStatus.reserved_tasks && (
            <AccordionItem value="reserved">
              <AccordionTrigger>
                <div className="flex items-center">
                  <IconDatabase className="mr-2" /> Reserved Tasks
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(workerStatus.reserved_tasks, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          )}
          {workerStatus.scheduled_tasks && (
            <AccordionItem value="scheduled">
              <AccordionTrigger>
                <div className="flex items-center">
                  <IconCloudComputing className="mr-2" /> Scheduled Tasks
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(workerStatus.scheduled_tasks, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          )}
          {workerStatus.registered_tasks && (
            <AccordionItem value="registered">
              <AccordionTrigger>
                <div className="flex items-center">
                  <IconReservedLine className="mr-2" /> Registered Tasks
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(workerStatus.registered_tasks, null, 2)}
                </pre>
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>
      ) : (
        <p className="text-sm text-muted-foreground">
          No worker status data available.
        </p>
      )}
    </>
  );
};

const CeleryQueue = ({
  queueInfo,
  load,
}: {
  queueInfo: any;
  load: (cache: boolean) => void;
}) => {
  return (
    <>
      <div className="flex justify-between my-4">
        <h1 className="flex items-center gap-4 text-2xl font-bold mb-6">
          Queue Info{" "}
          <button className="cursor-pointer" onClick={() => load(false)}>
            <IconRefresh />
          </button>
        </h1>
      </div>
      {queueInfo ? (
        <pre className="whitespace-pre-wrap text-sm">
          {JSON.stringify(queueInfo, null, 2)}
        </pre>
      ) : (
        <p className="text-sm text-muted-foreground">
          No queue info data available.
        </p>
      )}
    </>
  );
};
