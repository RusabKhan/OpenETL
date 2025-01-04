import { LogsConfig } from "@/types/integration";
import { useEffect, useRef } from "react";
import Spinner from "../common/Spinner";

interface LogPanelInterface {
  title: string;
  logsData: LogsConfig | undefined;
  isLoading: boolean;
  nextPage: () => void;
  previousPage: () => void;
}

const LogPanel = (params: LogPanelInterface) => {
  const { title, logsData, isLoading, nextPage, previousPage } = params;

  return (
    <div className="mx-auto rounded-lg bg-white p-4 text-black shadow-md dark:bg-boxdark dark:text-white">
      <h2 className="mb-4 text-lg font-bold">{title}</h2>
      <div className="h-[50vh] overflow-y-auto rounded-lg bg-gray-300 p-4 dark:bg-gray-800">
        {logsData && logsData.logs.length > 0 ? (
          <>
            {logsData.logs.map((log, index) => (
              <div
                key={index}
                className="mb-2 break-all rounded-md bg-gray-100 p-2 text-sm dark:bg-gray-700"
              >
                {log}
              </div>
            ))}
          </>
        ) : (
          <p className="text-gray-400">No logs available.</p>
        )}
      </div>
      <nav
        className="flex-column flex flex-wrap items-center justify-between pt-4 md:flex-row"
        aria-label="Table navigation"
      >
        <span className="mb-4 block w-full text-sm font-normal text-gray-500 dark:text-gray-400 md:mb-0 md:inline md:w-auto">
          Total Pages:{" "}
          <span className="font-semibold text-gray-900 dark:text-white">
            {logsData?.total_pages}
          </span>
        </span>
        <ul className="inline-flex h-8 -space-x-px text-sm rtl:space-x-reverse">
          <li>
            <button onClick={previousPage} className="ms-0 flex h-8 items-center justify-center rounded-s-lg border border-gray-300 bg-white px-3 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white">
              Previous
            </button>
          </li>
          <li>
            <span
              aria-current="page"
              className="flex h-8 items-center justify-center border border-gray-300 bg-blue-50 px-3 text-blue-600 hover:bg-blue-100 hover:text-blue-700 dark:border-gray-700 dark:bg-gray-700 dark:text-white"
            >
              {logsData?.page}
            </span>
          </li>
          <li>
            <button onClick={nextPage} className="flex h-8 items-center justify-center rounded-e-lg border border-gray-300 bg-white px-3 leading-tight text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white">
              Next
            </button>
          </li>
        </ul>
      </nav>
      <Spinner visible={isLoading} />
    </div>
  );
};

export default LogPanel;
