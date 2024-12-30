import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Celery | OpenETL Dashboard | Complex Pipelines Simplified",
  description: "OpenETL Dashboard makes complex pipelines simplified.",
};

const Celery = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Celery" />
    </DefaultLayout>
  );
};

export default Celery;
