"use client";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { WorkerTasks } from "@/types/tasks";
import { getCeleryTasks } from "@/utils/api";
import { useEffect, useState } from "react";

const Celery = () => {
  const [tasks, setTasks] = useState<WorkerTasks>({
    active_tasks: {},
    reserved_tasks: {},
    scheduled_tasks: {},
  });
  const [openSection, setOpenSection] = useState<number | null>(1);

  const toggleSection = (section: number) => {
    setOpenSection((prevSection) => (prevSection === section ? null : section));
  };

  useEffect(() => {
    const loadTasks = async () => {
      const res = await getCeleryTasks();
      setTasks(res);
    };
    loadTasks();
  }, []);

  return (
    <DefaultLayout>
      {/* <Breadcrumb pageName="Celery" /> */}

      <div id="accordion" data-accordion="open">
        {/* Section 1 */}
        <div>
          <h2 id="accordion-heading-1">
            <button
              type="button"
              className="flex w-full items-center justify-between gap-3 rounded-t-xl border border-b-0 border-gray-400 p-5 font-medium text-black hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:border-gray-700 dark:text-white dark:hover:bg-gray-800 dark:focus:ring-gray-800 rtl:text-right"
              onClick={() => toggleSection(1)}
              aria-expanded={openSection === 1}
              aria-controls="accordion-body-1"
            >
              <span className="flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="me-2 h-5 w-5 shrink-0"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
                  />
                </svg>
                Active Tasks
              </span>
              <svg
                className={`h-3 w-3 shrink-0 transition-transform ${
                  openSection === 1 ? "rotate-180" : ""
                }`}
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 10 6"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 5 5 1 1 5"
                />
              </svg>
            </button>
          </h2>
          <div
            id="accordion-body-1"
            className={`${
              openSection === 1 ? "block" : "hidden"
            } border border-b-0 border-gray-400 p-5 dark:border-gray-700`}
            aria-labelledby="accordion-heading-1"
          >
            <div>
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(tasks.active_tasks, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Section 2 */}
        <div>
          <h2 id="accordion-heading-2">
            <button
              type="button"
              className="flex w-full items-center justify-between gap-3 border border-b-0 border-gray-400 p-5 font-medium text-black hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:border-gray-700 dark:text-white dark:hover:bg-gray-800 dark:focus:ring-gray-800 rtl:text-right"
              onClick={() => toggleSection(2)}
              aria-expanded={openSection === 2}
              aria-controls="accordion-body-2"
            >
              <span className="flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="me-2 h-5 w-5 shrink-0"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125"
                  />
                </svg>
                Reserved Tasks
              </span>
              <svg
                className={`h-3 w-3 shrink-0 transition-transform ${
                  openSection === 2 ? "rotate-180" : ""
                }`}
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 10 6"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 5 5 1 1 5"
                />
              </svg>
            </button>
          </h2>
          <div
            id="accordion-body-2"
            className={`${
              openSection === 2 ? "block" : "hidden"
            } border border-b-0 border-gray-400 p-5 dark:border-gray-700`}
            aria-labelledby="accordion-heading-2"
          >
            <div>
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(tasks.reserved_tasks, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Section 3 */}
        <div>
          <h2 id="accordion-heading-3">
            <button
              type="button"
              className="flex w-full items-center justify-between gap-3 rounded-b-xl border border-gray-400 p-5 font-medium text-black hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:border-gray-700 dark:text-white dark:hover:bg-gray-800 dark:focus:ring-gray-800 rtl:text-right"
              onClick={() => toggleSection(3)}
              aria-expanded={openSection === 3}
              aria-controls="accordion-body-2"
            >
              <span className="flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="me-2 h-5 w-5 shrink-0"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z"
                  />
                </svg>
                Scheduled Tasks
              </span>
              <svg
                className={`h-3 w-3 shrink-0 transition-transform ${
                  openSection === 3 ? "rotate-180" : ""
                }`}
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 10 6"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 5 5 1 1 5"
                />
              </svg>
            </button>
          </h2>
          <div
            id="accordion-body-2"
            className={`${
              openSection === 3 ? "block" : "hidden"
            } rounded-b-xl border border-gray-400 p-5 dark:border-gray-700`}
            aria-labelledby="accordion-heading-2"
          >
            <div>
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(tasks.scheduled_tasks, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </DefaultLayout>
  );
};

export default Celery;
