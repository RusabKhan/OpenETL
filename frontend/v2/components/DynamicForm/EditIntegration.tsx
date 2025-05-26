import React, { useState } from "react";
import { update_integration } from "../utils/api";

interface DynamicFormProps {
  data: { [key: string]: any };
  closeForm: () => void;
  refresh: () => void;
}

const EditIntegration: React.FC<DynamicFormProps> = ({
  data,
  closeForm,
  refresh,
}) => {
  const [formData, setFormData] = useState(data);

  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (value === "false") {
      setFormData((prevData) => ({
        ...prevData,
        [name]: false,
      }));
    } else if (value === "true") {
      setFormData((prevData) => ({
        ...prevData,
        [name]: true,
      }));
    } else {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { id, is_enabled, is_running } = formData;

    const params = {
      pipeline_id: id,
      fields: {
        is_enabled,
        is_running,
      },
    };
    await update_integration(params);
    refresh();
    closeForm();
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={closeForm}></div>

      {/* Sidebar */}
      <div className="animate-in slide-in-from-right-5 relative h-full w-120 bg-background p-6 shadow-lg">
        {/* Close Button */}
        <button
          onClick={closeForm}
          className="absolute right-4 top-4 text-muted-foreground hover:text-foreground"
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
        <h2 className="mb-6 text-2xl font-bold text-foreground">Edit</h2>

        {/* Dynamic Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {Object.entries(formData).map(([key, value]) => {
            if (
              key !== "id" &&
              key !== "created_at" &&
              key !== "updated_at" &&
              key !== "cron_expression" &&
              key !== "integration_type"
            ) {
              return (
                <div key={key} className="flex flex-col">
                  <label
                    htmlFor={key}
                    className="text-sm font-medium capitalize text-foreground"
                  >
                    {key.replace("_", " ")}
                  </label>
                  <input
                    id={key}
                    name={key}
                    value={value}
                    onChange={handleChange}
                    className="mt-1 rounded-md border border-input bg-background p-2 text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  />
                </div>
              );
            }
          })}

          {/* Submit Button */}
          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              className="rounded-md bg-primary px-4 py-2 text-primary-foreground transition hover:bg-primary/90"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditIntegration;
