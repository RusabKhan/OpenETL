import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import TableThree from "@/components/Tables/TableThree";

const Integrations = () => {
  return (
    <>
      <DefaultLayout>
        <Breadcrumb pageName="List Integrations" />
        <TableThree />
      </DefaultLayout>
    </>
  );
};

export default Integrations;
