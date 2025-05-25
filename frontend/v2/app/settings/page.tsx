import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Link from "next/link";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Settings | OpenETL Dashboard",
  description: "Settings page for OpenETL dashboard",
};

const links = [
  {
    title: "Spark Worker",
    link: "http://localhost:8080",
    image: "https://cdn.dataomnisolutions.com/main/technology/spark.png",
    new_window: true,
  },
  {
    title: "API Docs",
    link: "http://localhost:5009/docs/",
    image: "https://cdn.dataomnisolutions.com/main/technology/fastapi.png",
    new_window: true,
  },
  {
    title: "Github",
    link: "https://github.com/RusabKhan/OpenETL.git",
    image:
      "https://cdn.dataomnisolutions.com/main/connector_logos/github-tile.svg",
    new_window: true,
  },
  {
    title: "Support",
    link: "https://github.com/RusabKhan/OpenETL/issues",
    image:
      "https://cdn.dataomnisolutions.com/main/connector_logos/github-icon.svg",
    new_window: true,
  },
];

const Settings = () => {
  return (
    <DefaultLayout title="Settings">
      <div className="p-4 md:p-6 grid grid-cols-1 sm:grid-cols-2 gap-6 md:grid-cols-4 lg:grid-cols-6">
        {links.map((url, i) => (
          <Card
            className="@container/card text-left w-full cursor-pointer p-0"
            key={i}
          >
            <CardHeader className="p-0">
              <Link
                href={url.link}
                target={url.new_window ? "_blank" : "_self"}
              >
                <div className="flex h-40 flex-col items-center justify-center">
                  <CardDescription className="flex flex-row items-center gap-2">
                    {url.image && (
                      <img src={url.image} width={80} height={100} alt="logo" />
                    )}
                  </CardDescription>
                  <CardTitle className="text-xl font-semibold tabular-nums">
                    <h3 className="text-center font-medium text-black dark:text-gray-200">
                      {url.title}
                    </h3>
                  </CardTitle>
                </div>
              </Link>
            </CardHeader>
          </Card>
        ))}
      </div>
    </DefaultLayout>
  );
};

export default Settings;
