import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Spark | OpenETL Dashboard | Complex Pipelines Simplified",
  description: "OpenETL Dashboard makes complex pipelines simplified.",
};

const Spark = () => {
  return (
    <DefaultLayout title="Spark | OpenETL">
      <Breadcrumb pageName="Spark" />
    </DefaultLayout>
  );
};

export default Spark;
