"use client";

import React, { useEffect, useState } from "react";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { useRouter } from "next/navigation";
import { IntegrationConfig } from "@/components/types/integration";
import { getCurrentDate, getCurrentTime } from "@/components/utils/func";
import { create_integration } from "@/components/utils/api";
import { toast } from "sonner";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import SourceTargetTab from "@/components/pipelines/source";
import SparkConfigTab from "@/components/pipelines/spark";
import FinishTab from "@/components/pipelines/finish";

const tabs = ["Select Source & Target", "Spark/Hadoop Config", "Finish"];

const initial_integration: IntegrationConfig = {
  frequency: "Weekly",
  hadoop_config: {},
  integration_name: "",
  integration_type: "full_load",
  schedule_date: [getCurrentDate()],
  schedule_time: getCurrentTime(),
  source_connection: 0,
  source_schema: "",
  source_table: "",
  spark_config: {
    "spark.app.name": "",
    "spark.driver.memory": "1g",
    "spark.executor.cores": "1",
    "spark.executor.instances": "1",
    "spark.executor.memory": "1g",
  },
  target_connection: 0,
  target_schema: "",
  target_table: "",
  batch_size: 100000,
};

const CreateEtl = () => {
  const [activeTab, setActiveTab] = useState("selectsource&target");
  const [integration, setIntegration] =
    useState<IntegrationConfig>(initial_integration);
  const router = useRouter();

  const handleNextTab = () => {
    if (activeTab === "selectsource&target") {
      setActiveTab("spark/hadoopconfig");
    } else if (activeTab === "spark/hadoopconfig") {
      setActiveTab("finish");
    }
  };

  const handlePreviousTab = () => {
    if (activeTab === "spark/hadoopconfig") {
      setActiveTab("selectsource&target");
    } else if (activeTab === "finish") {
      setActiveTab("spark/hadoopconfig");
    }
  };

  const handleCreateIntegration = async () => {
    try {
      const res = await create_integration(integration);
      if (res && 'status' in res && res.status === 201) {
        toast.success("Integration created successfully!");
        router.push("/pipelines");
      } else if (res && 'status' in res && res.status === 409) {
        toast.error("Integration name already exists!");
      } else {
        toast.error("Failed to create integration.");
      }
    } catch (error: any) {
      toast.error(error.message || "Failed to create integration.");
    }
  };

  useEffect(() => {
    document.title = "Create ETL | OpenETL";
  }, []);

  return (
    <DefaultLayout title="Pipelines">
      <div className="p-4 md:p-6">
        <div className="pb-4 md:pb-6">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Home</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink href="/pipelines">Pipelines</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Create ETL Pipeline</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value)}>
          <TabsList className="flex mb-4 gap-4 border-b border-gray-300 dark:border-gray-700">
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab}
                value={tab.toLowerCase().replace(/ /g, "")}
                className={`px-4 py-2 text-sm font-medium ${activeTab === tab.toLowerCase().replace(/ /g, "")
                  ? "border-b-2 border-blue-500 text-blue-500 dark:text-blue-400"
                  : "text-gray-600 dark:text-gray-400"
                  }`}
              >
                {tab}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Tab Content */}
        </Tabs>

        {activeTab === "selectsource&target" && (
          <SourceTargetTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}
        {activeTab === "spark/hadoopconfig" && (
          <SparkConfigTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}
        {activeTab === "finish" && (
          <FinishTab
            integration={integration}
            setIntegration={setIntegration}
          />
        )}
        {/* Navigation Buttons */}
        <div className="mt-6 flex justify-between">
          {activeTab !== "selectsource&target" && (
            <Button variant="outline" onClick={handlePreviousTab}>
              Previous
            </Button>
          )}
          {activeTab !== "finish" && (
            <Button onClick={handleNextTab} variant="secondary">
              Next
            </Button>
          )}
          {activeTab === "finish" && (
            <Button onClick={handleCreateIntegration}>
              Create Integration
            </Button>
          )}
        </div>
      </div>
    </DefaultLayout>
  );
};

export default CreateEtl;
