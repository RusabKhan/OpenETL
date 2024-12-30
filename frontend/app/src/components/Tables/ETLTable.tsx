import { ListIntegrationConfig } from "@/types/integration";
import EditIntegration from "../DynamicForm/EditIntegration";
import { useState } from "react";
import Link from "next/link";

interface ETLTableInterface {
  columns: string[];
  data?: ListIntegrationConfig[];
  load: () => void;
}

const ETLTable: React.FC<ETLTableInterface> = (params) => {
  const { columns, data, load } = params;
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="relative overflow-x-auto shadow-md sm:rounded-lg">
      <table className="w-full text-left text-sm text-gray-500 dark:text-gray-400 rtl:text-right">
        <thead className="bg-gray-50 text-xs uppercase text-gray-700 dark:bg-gray-700 dark:text-gray-400">
          <tr>
            <th scope="col" className="p-4">
              <div className="flex items-center">
                <input
                  id="checkbox-all-search"
                  type="checkbox"
                  className="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600 dark:focus:ring-offset-gray-800"
                />
                <label className="sr-only">checkbox</label>
              </div>
            </th>
            {columns.map((column, i) => (
              <th key={i} scope="col" className="px-6 py-3">
                {column}
              </th>
            ))}
            <th scope="col" className="px-6 py-3">
              Action
            </th>
          </tr>
        </thead>

        <tbody>
          {data?.map((integration, key) => (
            <tr
              key={key}
              className="border-b bg-white hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-600"
            >
              <td className="w-4 p-4">
                <div className="flex items-center">
                  <input
                    id="checkbox-table-search-1"
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 bg-gray-100 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600 dark:focus:ring-offset-gray-800"
                  />
                  <label className="sr-only">checkbox</label>
                </div>
              </td>
              <td className="px-6 py-4">
                <Link href={`/integrations/${integration.id}`}>
                  {integration.id}
                </Link>
              </td>
              <td className="y-4 break-all px-6">
                {integration.integration_name}
              </td>
              <td className="px-6 py-4">{integration.integration_type}</td>
              <td className="px-6 py-4">
                {integration.cron_expression.map((cron) => (
                  <span>{cron.cron_expression}</span>
                ))}
              </td>
              <td className="px-6 py-4">
                {integration.cron_expression.map((cron) => (
                  <span>{cron.explanation}</span>
                ))}
              </td>
              <td className="px-6 py-4">
                <p
                  className={`inline-flex rounded-full bg-opacity-10 px-3 py-1 text-sm font-medium ${
                    integration.is_enabled
                      ? "bg-success text-success"
                      : "bg-danger text-danger"
                  }`}
                >
                  {integration.is_enabled ? "Active" : "Not Active"}
                </p>
              </td>
              <td className="px-6 py-4">
                <p
                  className={`inline-flex rounded-full bg-opacity-10 px-3 py-1 text-sm font-medium ${
                    integration.is_running
                      ? "bg-success text-success"
                      : "bg-danger text-danger"
                  }`}
                >
                  {integration.is_running ? "Running" : "Stopped"}
                </p>
              </td>
              <td className="px-6 py-4">
                <button
                  onClick={() => {
                    setShowForm(true);
                  }}
                  className="font-medium text-blue-600 hover:underline dark:text-blue-500"
                >
                  Edit
                </button>
              </td>
              {showForm && (
                <EditIntegration
                  data={integration}
                  closeForm={() => {
                    load();
                    setShowForm(false);
                  }}
                />
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ETLTable;
