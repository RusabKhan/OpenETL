"use client";

import { useState } from "react";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

const CreateEtl = () => {
  const [activeTab, setActiveTab] = useState("selectsource&target");

  const handleNextTab = () => {
    if (activeTab === "selectsource&target") {
      setActiveTab("sparkconfig");
    } else if (activeTab === "sparkconfig") {
      setActiveTab("finish");
    }
  };

  const handlePreviousTab = () => {
    if (activeTab === "sparkconfig") {
      setActiveTab("selectsource&target");
    } else if (activeTab === "finish") {
      setActiveTab("sparkconfig");
    }
  };

  return (
    <DefaultLayout>
      <div className="mx-auto max-w-7xl p-6">
        <Breadcrumb pageName="Create ETL" />

        {/* Tabs */}
        <div className="flex gap-4 border-b border-gray-300 mb-6">
          {["Select Source & Target", "Spark/Hadoop Config", "Finish"].map((tab) => (
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
        {activeTab === "spark/hadoopconfig" && <SparkConfigTab />}
        {activeTab === "finish" && <FinishTab />}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-6">
          {activeTab !== "selectsource&target" && (
            <button
              onClick={handlePreviousTab}
              className="bg-gray-300 text-gray-700 py-2 px-4 rounded"
            >
              Previous
            </button>
          )}
          {activeTab !== "finish" && (
            <button
              onClick={handleNextTab}
              className="bg-blue-500 text-white py-2 px-4 rounded"
            >
              Next
            </button>
          )}
          {activeTab === "finish" && (
            <button
              onClick={() => alert("ETL Integration Created!")}
              className="bg-green-500 text-white py-2 px-4 rounded"
            >
              Create Integration
            </button>
          )}
        </div>
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

// Spark/Hadoop Config Tab
// const SparkConfigTab = () => {
//   const [sparkConfig, setSparkConfig] = useState([
//     { config: "spark.driver.memory", value: "1g", isEditing: false },
//     { config: "spark.executor.memory", value: "1g", isEditing: false },
//     { config: "spark.executor.cores", value: "1", isEditing: false },
//     { config: "spark.executor.instances", value: "1", isEditing: false },
//     { config: "spark.app.name", value: "my_connection_to_my_connection", isEditing: false },
//   ]);

//   const [hadoopConfig, setHadoopConfig] = useState([
//     { config: "fs.defaultFS", value: "hdfs://localhost:8020", isEditing: false },
//     { config: "dfs.replication", value: "3", isEditing: false },
//     { config: "yarn.nodemanager.memory-mb", value: "2048", isEditing: false },
//     { config: "mapreduce.framework.name", value: "yarn", isEditing: false },
//     { config: "hadoop.tmp.dir", value: "/tmp/hadoop", isEditing: false },
//   ]);

//   const handleEdit = (setConfig: any, index: any) => {
//     setConfig((prev: any) =>
//       prev.map((item: any, idx: any) =>
//         idx === index ? { ...item, isEditing: !item.isEditing } : item
//       )
//     );
//   };

//   const handleChange = (setConfig: any, index: any, newValue: any) => {
//     setConfig((prev: any) =>
//       prev.map((item: any, idx: any) =>
//         idx === index ? { ...item, value: newValue } : item
//       )
//     );
//   };

//   const renderTable = (data: any, setConfig: any) => (
//     <table className="w-full border-collapse border border-gray-300">
//       <thead>
//         <tr>
//           <th className="border border-gray-300 px-4 py-2">Configuration</th>
//           <th className="border border-gray-300 px-4 py-2">Value</th>
//           <th className="border border-gray-300 px-4 py-2">Actions</th>
//         </tr>
//       </thead>
//       <tbody>
//         {data.map((row: any, index: any) => (
//           <tr key={row.config}>
//             <td className="border border-gray-300 px-4 py-2">{row.config}</td>
//             <td className="border border-gray-300 px-4 py-2">
//               {row.isEditing ? (
//                 <input
//                   type="text"
//                   value={row.value}
//                   onChange={(e) => handleChange(setConfig, index, e.target.value)}
//                   className="w-full border border-gray-300 px-2 py-1"
//                 />
//               ) : (
//                 row.value
//               )}
//             </td>
//             <td className="border border-gray-300 px-4 py-2 text-center">
//               <button
//                 onClick={() => handleEdit(setConfig, index)}
//                 className="text-blue-500 hover:text-blue-700 flex items-center justify-center"
//               >
//                 {row.isEditing ? (
//                   // Check icon (SVG)
//                   <svg
//                     className="h-5 w-5"
//                     xmlns="http://www.w3.org/2000/svg"
//                     viewBox="0 0 24 24"
//                     fill="none"
//                     stroke="currentColor"
//                   >
//                     <path
//                       strokeLinecap="round"
//                       strokeLinejoin="round"
//                       strokeWidth="2"
//                       d="M5 13l4 4L19 7"
//                     />
//                   </svg>
//                 ) : (
//                   // Pencil icon (SVG)
//                   <svg
//                     className="h-5 w-5"
//                     xmlns="http://www.w3.org/2000/svg"
//                     viewBox="0 0 20 20"
//                     fill="currentColor"
//                   >
//                     <path
//                       fillRule="evenodd"
//                       d="M17.121 2.879a3 3 0 00-4.242 0L5 9.244V12h2.756l8.879-8.879a3 3 0 000-4.242zM3 14v3h3l8.879-8.879a3 3 0 000-4.242l-1.5-1.5a3 3 0 00-4.242 0L3 10.756V14z"
//                       clipRule="evenodd"
//                     />
//                   </svg>
//                 )}
//               </button>
//             </td>
//           </tr>
//         ))}
//       </tbody>
//     </table>
//   );

//   return (
//     <div>
//       <div className="grid grid-cols-2 gap-8">
//         <div>
//           <h3 className="text-md font-semibold mb-2">Spark Configuration</h3>
//           {renderTable(sparkConfig, setSparkConfig)}
//         </div>
//         <div>
//           <h3 className="text-md font-semibold mb-2">Hadoop Configuration</h3>
//           {renderTable(hadoopConfig, setHadoopConfig)}
//         </div>
//       </div>
//     </div>
//   );
// };

const SparkConfigTab = () => {
  const [sparkConfig, setSparkConfig] = useState([
    { config: "spark.driver.memory", value: "1g", isEditing: false },
    { config: "spark.executor.memory", value: "1g", isEditing: false },
    { config: "spark.executor.cores", value: "1", isEditing: false },
    { config: "spark.executor.instances", value: "1", isEditing: false },
    { config: "spark.app.name", value: "my_connection_to_my_connection", isEditing: false },
  ]);

  const [hadoopConfig, setHadoopConfig] = useState([
    { config: "fs.defaultFS", value: "hdfs://localhost:8020", isEditing: false },
    { config: "dfs.replication", value: "3", isEditing: false },
    { config: "yarn.nodemanager.memory-mb", value: "2048", isEditing: false },
    { config: "mapreduce.framework.name", value: "yarn", isEditing: false },
    { config: "hadoop.tmp.dir", value: "/tmp/hadoop", isEditing: false },
  ]);

  // Add a new row to the table
  const handleAddRow = (setConfig: any) => {
    setConfig((prev: any) => [
      ...prev,
      { config: "new.config.key", value: "new_value", isEditing: true },
    ]);
  };

  // Delete a row from the table
  const handleDeleteRow = (setConfig: any, index: any) => {
    setConfig((prev: any) => prev.filter((_, idx: any) => idx !== index));
  };

  const handleEdit = (setConfig: any, index: any) => {
    setConfig((prev: any) =>
      prev.map((item: any, idx: any) =>
        idx === index ? { ...item, isEditing: !item.isEditing } : item
      )
    );
  };

  const handleChange = (setConfig: any, index: any, newValue: any) => {
    setConfig((prev: any) =>
      prev.map((item: any, idx: any) =>
        idx === index ? { ...item, value: newValue } : item
      )
    );
  };

  const renderTable = (data: any, setConfig: any) => (
    <table className="w-full border-collapse border border-gray-300">
      <thead>
        <tr>
          <th className="border border-gray-300 px-4 py-2">Configuration</th>
          <th className="border border-gray-300 px-4 py-2">Value</th>
          <th className="border border-gray-300 px-4 py-2">Actions</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row: any, index: any) => (
          <tr key={`${row.config}-${index}`}>
            <td className="border border-gray-300 px-4 py-2">
              {row.isEditing ? (
                <input
                  type="text"
                  value={row.config}
                  onChange={(e) =>
                    setConfig((prev: any) =>
                      prev.map((item: any, idx: any) =>
                        idx === index ? { ...item, config: e.target.value } : item
                      )
                    )
                  }
                  className="w-full border border-gray-300 px-2 py-1"
                />
              ) : (
                row.config
              )}
            </td>
            <td className="border border-gray-300 px-4 py-2">
              {row.isEditing ? (
                <input
                  type="text"
                  value={row.value}
                  onChange={(e) => handleChange(setConfig, index, e.target.value)}
                  className="w-full border border-gray-300 px-2 py-1"
                />
              ) : (
                row.value
              )}
            </td>
            <td className="border border-gray-300 px-4 py-2 text-center flex justify-center items-center gap-2">
              <button
                onClick={() => handleEdit(setConfig, index)}
                className="text-blue-500 hover:text-blue-700 flex items-center"
              >
                {row.isEditing ? (
                  // Check icon
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  // Pencil icon
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M17.121 2.879a3 3 0 00-4.242 0L5 9.244V12h2.756l8.879-8.879a3 3 0 000-4.242zM3 14v3h3l8.879-8.879a3 3 0 000-4.242l-1.5-1.5a3 3 0 00-4.242 0L3 10.756V14z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
              <button
                onClick={() => handleDeleteRow(setConfig, index)}
                className="text-red-500 hover:text-red-700 flex items-center"
              >
                {/* Trash icon */}
                <svg
                  className="h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 7l-1 14H6L5 7m5 4v6m4-6v6m1-9V5a1 1 0 00-1-1h-4a1 1 0 00-1 1v1m-4 0h14"
                  />
                </svg>
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div>
      <div className="grid grid-cols-2 gap-8">
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-md font-semibold">Spark Configuration</h3>
            <button
              onClick={() => handleAddRow(setSparkConfig)}
              className="text-green-500 hover:text-green-700 flex items-center"
            >
              {/* Add icon */}
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
          {renderTable(sparkConfig, setSparkConfig)}
        </div>
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-md font-semibold">Hadoop Configuration</h3>
            <button
              onClick={() => handleAddRow(setHadoopConfig)}
              className="text-green-500 hover:text-green-700 flex items-center"
            >
              {/* Add icon */}
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>
          {renderTable(hadoopConfig, setHadoopConfig)}
        </div>
      </div>
    </div>
  );
}

// Finish Tab
const FinishTab = () => (
  <div>
    <h2 className="text-lg font-semibold mb-4">Finish</h2>
    <div className="grid gap-4">
      <div>
        <label className="block text-sm font-medium mb-1">
          Enter unique integration name
        </label>
        <input
          type="text"
          className="w-full p-2 border rounded"
          placeholder="Enter integration name"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Select Schedule Type</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="scheduleType"
              value="frequency"
              defaultChecked
              className="mr-2"
            />
            Frequency
          </label>
          <label className="flex items-center">
            <input type="radio" name="scheduleType" value="selectedDates" className="mr-2" />
            Selected Dates
          </label>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Select Frequency</label>
        <select className="w-full p-2 border rounded">
          <option value="weekly">Weekly</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Select Integration Type</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              name="integrationType"
              value="fullLoad"
              defaultChecked
              className="mr-2"
            />
            Full Load
          </label>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Schedule Date</label>
        <input
          type="date"
          className="w-full p-2 border rounded"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Schedule Time</label>
        <input
          type="time"
          className="w-full p-2 border rounded"
          defaultValue="19:05"
        />
      </div>
      <button className="bg-blue-500 text-white py-2 px-4 rounded">
        Create Integration
      </button>
    </div>
  </div>
);

export default CreateEtl;
