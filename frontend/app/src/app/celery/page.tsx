"use client";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { getCeleryTasks } from "@/utils/api";
import { Metadata } from "next";
import { useEffect, useState } from "react";

// export const metadata: Metadata = {
//   title: "Celery | OpenETL Dashboard | Complex Pipelines Simplified",
//   description: "OpenETL Dashboard makes complex pipelines simplified.",
// };

const Celery = () => {
  const [jobs, setJobs] = useState({
    jobs: [],
  });

  useEffect(() => {
    const loadJobs = async () => {
      const res = await getCeleryTasks();
      console.log(res);
      setJobs(res);
    };
    loadJobs();
  }, []);

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Celery" />
    </DefaultLayout>
  );
};

export default Celery;
