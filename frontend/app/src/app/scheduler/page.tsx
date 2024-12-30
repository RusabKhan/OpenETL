import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Scheduler | OpenETL Dashboard | Complex Pipelines Simplified",
  description: "OpenETL Dashboard makes complex pipelines simplified.",
};

const Scheduler = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Scheduler" />
    </DefaultLayout>
  );
};

export default Scheduler;
