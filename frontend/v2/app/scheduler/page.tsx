"use client";

import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Spinner from "@/components/Spinner";
import { Table, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getSchedulerListJobs } from "@/components/utils/api";
import { IconRefresh } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function Scheduler() {
  const [job, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const load = async (cache: boolean) => {
    try {
      setIsLoading(true);
      const res = await getSchedulerListJobs(cache);
      setJobs(res.data);
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    document.title = "Scheduler | OpenETL";

    load(true);
  }, []);

  return (
    <DefaultLayout title="Scheduler">
      <div className="p-4 md:p-6">
        <h1 className="flex items-center gap-4 text-2xl font-bold mb-6">
          Scheduler Jobs{" "}
          <button className="cursor-pointer" onClick={() => load(false)}>
            <IconRefresh />
          </button>
        </h1>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="p-4">

                </TableHead>
              </TableRow>
            </TableHeader>
          </Table>
        </div>
      </div>
      <Spinner visible={isLoading} />
    </DefaultLayout>
  );
}
