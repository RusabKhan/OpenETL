import { update_connection } from "@/utils/api";
import React, { useState } from "react";

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
    parentKey: string,
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
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={closeForm}
      ></div>

      {/* Sidebar */}
      <div className="overflow-y-scroll animate-slide-in-right relative h-full w-96 bg-white p-6 shadow-lg dark:bg-boxdark">
        {/* Close Button */}
        <button
          onClick={closeForm}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="2"
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Title */}
        <h2 className="mb-6 text-2xl font-bold text-gray-800 dark:text-white">
          Edit
        </h2>

        {/* Dynamic Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {Object.entries(formData).map(([key, value]) => {
            if (key !== "id") {
              // Check if the value is an object (nested)
              if (typeof value === "object" && value !== null) {
                return (
                  <div key={key} className="space-y-2">
                    <h3 className="text-sm font-bold capitalize text-gray-700 dark:text-white">
                      {key.replace("_", " ")}
                    </h3>
                    {Object.entries(value).map(([nestedKey, nestedValue]) => (
                      <div
                        key={`${key}.${nestedKey}`}
                        className="flex flex-col"
                      >
                        <label
                          htmlFor={`${key}.${nestedKey}`}
                          className="text-sm font-medium capitalize text-gray-700 dark:text-white"
                        >
                          {nestedKey.replace("_", " ")}
                        </label>
                        <input
                          id={`${key}.${nestedKey}`}
                          name={nestedKey}
                          value={nestedValue as string}
                          onChange={
                            (e) => handleNestedChange(e, key) // Pass the parent key to the nested handler
                          }
                          className="mt-1 rounded border bg-whiten p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-boxdark"
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
                      className="text-sm font-medium capitalize text-gray-700 dark:text-white"
                    >
                      {key.replace("_", " ")}
                    </label>
                    <input
                      id={key}
                      name={key}
                      value={value}
                      onChange={handleChange}
                      className="mt-1 rounded border bg-whiten p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-boxdark"
                    />
                  </div>
                );
              }
            }
            return null; // For keys like "id" or any other excluded fields
          })}

          {/* Submit Button */}
          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              className="rounded bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
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
