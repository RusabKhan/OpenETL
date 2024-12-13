"use client";

import { useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

const CreateEtl = () => {
  const [activeTab, setActiveTab] = useState("selectsource&target");

  console.log('activeTab', activeTab)
  return (
    <DefaultLayout>
      <div className="mx-auto max-w-7xl p-6">
        <Breadcrumb pageName="Create ETL" />

        {/* Tabs */}
        <div className="flex gap-4 border-b border-gray-300 mb-6">
          {["Select Source & Target", "Spark Config", "Finish"].map((tab) => (
            <button
              key={tab}
              className={`py-2 px-4 text-sm font-medium ${
                activeTab === tab.toLowerCase().replace(/ /g, "")
                  ? "border-b-2 border-blue-500 text-blue-500"
                  : "text-gray-600"
              }`}
              onClick={() => setActiveTab(tab.toLowerCase().replace(/ /g, ""))}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "selectsource&target" && <SourceTargetTab />}
        {activeTab === "sparkConfig" && <SparkConfigTab />}
        {activeTab === "finish" && <FinishTab />}
      </div>
    </DefaultLayout>
  );
};

// Source & Target Tab
const SourceTargetTab = () => (
  <div className="space-y-6">
    {/* Source Section */}
    <div className="border p-6 rounded-lg">
      <h2 className="text-lg font-semibold mb-4">Source</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Source</label>
          <select className="w-full p-2 border rounded">
            <option value="my_connection">my_connection</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Source Schema</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value="public"
            readOnly
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Source Tables</label>
          <select className="w-full p-2 border rounded">
            <option value="apscheduler_jobs">apscheduler_jobs</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Source Type</label>
          <div className="flex items-center gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="sourceType"
                value="database"
                defaultChecked
                className="mr-2"
              />
              Database
            </label>
            <label className="flex items-center">
              <input type="radio" name="sourceType" value="api" className="mr-2" />
              API
            </label>
          </div>
        </div>
      </div>
    </div>

    {/* Target Section */}
    <div className="border p-6 rounded-lg">
      <h2 className="text-lg font-semibold mb-4">Target</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Target</label>
          <select className="w-full p-2 border rounded">
            <option value="my_connection">my_connection</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target Schema</label>
          <input
            type="text"
            className="w-full p-2 border rounded"
            value="public"
            readOnly
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target Tables</label>
          <select className="w-full p-2 border rounded">
            <option value="new">New</option>
            <option value="existing">Existing</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target Type</label>
          <div className="flex items-center gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="targetType"
                value="database"
                defaultChecked
                className="mr-2"
              />
              Database
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Spark Config Tab
const SparkConfigTab = () => (
  <div>
    <h2 className="text-lg font-semibold">Spark Config</h2>
    <p>Configure Spark-related settings here.</p>
  </div>
);

// Finish Tab
const FinishTab = () => (
  <div>
    <h2 className="text-lg font-semibold">Finish</h2>
    <p>Review and finalize your ETL configuration.</p>
  </div>
);

export default CreateEtl;
