"use client";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { getSchedulerListJobs } from "@/utils/api";
import { Metadata } from "next";
import { useEffect, useState } from "react";

// export const metadata: Metadata = {
//   title: "Scheduler | OpenETL Dashboard | Complex Pipelines Simplified",
//   description: "OpenETL Dashboard makes complex pipelines simplified.",
// };

const Scheduler = () => {
  const [jobs, setJobs] = useState({
    jobs: [],
  });

  useEffect(() => {
    const loadJobs = async () => {
      const res = await getSchedulerListJobs();
      console.log(res);
      setJobs(res);
    };
    loadJobs();
  }, []);

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Scheduler" />
    </DefaultLayout>
  );
};

export default Scheduler;
