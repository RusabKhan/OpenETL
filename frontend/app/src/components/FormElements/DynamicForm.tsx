"use client";

import React from "react";

interface FormData {
  [key: string]: string | number;
}

interface ApiResponse {
  [section: string]: FormData;
}

interface DynamicFieldRendererProps {
  apiResponse: ApiResponse;
  formData: ApiResponse;
  setFormData: React.Dispatch<React.SetStateAction<ApiResponse>>;
}

const DynamicFieldRenderer: React.FC<DynamicFieldRendererProps> = ({
  apiResponse,
  formData,
  setFormData,
}) => {
  const handleInputChange = (
    section: string,
    key: string,
    value: string | number,
  ) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
  };

  return (
    <>
      {Object.entries(apiResponse).map(([section, fields]) => (
        <div key={section} className="mb-6 border-b pb-4">
          <h2 className="mb-2 text-xl font-bold capitalize">{section}</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {Object.entries(fields).map(([key, value]) => (
              <div key={key} className="flex flex-col">
                <label htmlFor={`${section}-${key}`} className="font-medium">
                  {key}
                </label>
                <input
                  id={`${section}-${key}`}
                  type={typeof value === "number" ? "number" : "text"}
                  value={formData[section][key]}
                  onChange={(e) =>
                    handleInputChange(
                      section,
                      key,
                      typeof value === "number"
                        ? +e.target.value
                        : e.target.value,
                    )
                  }
                  className="rounded border p-2"
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  );
};

export default DynamicFieldRenderer;
