import React, { useState } from "react";
import { update_connection } from "../utils/api";
import { Input } from "../ui/input";

interface DynamicFormProps {
  data: { [key: string]: any };
  closeForm: () => void;
}

const EditConnection: React.FC<DynamicFormProps> = ({ data, closeForm }) => {
  const [formData, setFormData] = useState(data);

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleNestedChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    parentKey: string
  ) => {
    const { name, value } = e.target;

    setFormData((prevData) => ({
      ...prevData,
      [parentKey]: {
        ...prevData[parentKey],
        [name]: value,
      },
    }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Destructure id and rest of form data
    const { id, ...fields } = formData;

    const params = {
      document_id: id,
      fields,
    };
    await update_connection(params);
    closeForm();
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={closeForm}></div>

      {/* Sidebar */}
      <div className="animate-slide-in-right relative h-full w-120 bg-white p-4 shadow-lg dark:bg-neutral-900 overflow-y-scroll">
        {/* Close Button */}
        <button
          onClick={closeForm}
          className="absolute right-3 top-3 text-neutral-400 hover:text-neutral-600 dark:text-neutral-500 dark:hover:text-neutral-300"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="2"
            stroke="currentColor"
            className="h-5 w-5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Title */}
        <h2 className="mb-4 text-xl font-bold text-neutral-800 dark:text-neutral-100">
          Edit
        </h2>

        {/* Dynamic Form */}
        <form onSubmit={handleSubmit} className="space-y-3">
          {Object.entries(formData).map(([key, value]) => {
            if (key !== "id") {
              // Check if the value is an object (nested)
              if (typeof value === "object" && value !== null) {
                return (
                  <div key={key} className="space-y-1">
                    <h3 className="text-xs font-bold capitalize text-neutral-700 dark:text-neutral-300">
                      {key.replace("_", " ")}
                    </h3>
                    {Object.entries(value).map(([nestedKey, nestedValue]) => (
                      <div
                        key={`${key}.${nestedKey}`}
                        className="flex flex-col"
                      >
                        <label
                          htmlFor={`${key}.${nestedKey}`}
                          className="text-xs font-medium capitalize text-neutral-700 dark:text-neutral-300"
                        >
                          {nestedKey.replace("_", " ")}
                        </label>
                        <Input
                          id={`${key}.${nestedKey}`}
                          name={nestedKey}
                          type={key === "password" || nestedKey === "password" ? "password" : "text"}
                          value={nestedValue as string}
                          onChange={
                            (e) => handleNestedChange(e, key) // Pass the parent key to the nested handler
                          }
                          className="mt-1 rounded border border-neutral-300 bg-white p-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
                        />
                      </div>
                    ))}
                  </div>
                );
              } else {
                // Handle top-level properties
                return (
                  <div key={key} className="flex flex-col">
                    <label
                      htmlFor={key}
                      className="text-xs font-medium capitalize text-neutral-700 dark:text-neutral-300"
                    >
                      {key.replace("_", " ")}
                    </label>
                    <Input
                      id={key}
                      name={key}
                      type={key === "password" ? "password" : "text"}
                      value={value}
                      onChange={handleChange}
                      className="mt-1 rounded border border-neutral-300 bg-white p-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
                    />
                  </div>
                );
              }
            }
            return null; // For keys like "id" or any other excluded fields
          })}

          {/* Submit Button */}
          <div className="mt-4 flex justify-end">
            <button
              type="submit"
              className="rounded bg-blue-500 px-3 py-1 text-sm text-white transition hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditConnection;
