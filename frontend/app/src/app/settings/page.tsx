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
    image: "https://cdn.dataomnisolutions.com/main/technology/spark.png",
  },
  {
    title: "API Docs",
    link: "http://localhost:5009/docs/",
    image: "https://cdn.dataomnisolutions.com/main/technology/fastapi.png",
  },
  {
    title: "Github",
    link: "https://github.com/RusabKhan/OpenETL.git",
    image:
      "https://cdn.dataomnisolutions.com/main/connector_logos/github-tile.svg",
  },
  {
    title: "Support",
    link: "https://github.com/RusabKhan/OpenETL/issues",
    image:
      "https://cdn.dataomnisolutions.com/main/connector_logos/github-icon.svg",
  },
];

const Settings = () => {
  return (
    <DefaultLayout>
      {/* <Breadcrumb pageName="Settings" /> */}

      <div className="grid grid-cols-4 gap-8">
        {links.map((url, i) => (
          <div className="col-span-1" key={i}>
            <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
              <Link href={url.link} target="_blank">
                <div className="flex flex-col items-center justify-center h-40 border-b border-stroke px-7 py-10 dark:border-strokedark">
                  <Image src={url.image} width={80} height={100} alt="logo" />
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
