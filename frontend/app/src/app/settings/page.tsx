import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import Image from "next/image";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Settings | OpenETL Dashboard",
  description: "Settings page for OpenETL dashboard",
};

const links = [
  {
    title: "Spark Worker",
    link: "http://localhost:8080",
  },
  {
    title: "API Docs",
    link: "http://localhost:5009/docs/",
  },
  {
    title: "Github",
    link: "https://github.com/RusabKhan/OpenETL.git",
  },
  {
    title: "Support",
    link: "https://github.com/RusabKhan/OpenETL/issues",
  },
];

const Settings = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Settings" />

      <div className="grid grid-cols-4 gap-8">
        {links.map((url, i) => (
          <div className="col-span-1" key={i}>
            <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
              <Link href={url.link} target="_blank">
                <div className="border-b border-stroke px-7 py-10 dark:border-strokedark">
                  <h3 className="text-center font-medium text-black dark:text-white">
                    {url.title}
                  </h3>
                </div>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </DefaultLayout>
  );
};

export default Settings;
