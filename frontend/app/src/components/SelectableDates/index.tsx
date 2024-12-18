import { IntegrationConfig } from "@/types/integration";
import React, { Dispatch, SetStateAction, useEffect, useState } from "react";

interface SelectableDatesInterface {
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}

const SelectableDates: React.FC<SelectableDatesInterface> = (params) => {
  const { integration, setIntegration } = params;
  const [selectedDates, setSelectedDates] = useState<string[]>(
    integration.schedule_date,
  );
  const [inputValue, setInputValue] = useState<string>("");
  const [dropdownOptions, setDropdownOptions] = useState<string[]>([]);

  // Add date to selected list
  const addDate = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputValue.trim() !== "") {
      setSelectedDates([...selectedDates, inputValue.trim()]);
      setInputValue("");
      setDropdownOptions([]); // Clear dropdown suggestions
    }
  };

  useEffect(() => {
    setIntegration((prev) => ({
      ...prev,
      schedule_date: selectedDates,
    }));
  }, [selectedDates]);

  // Remove a specific date
  const removeDate = (date: string) => {
    setSelectedDates(selectedDates.filter((d) => d !== date));
  };

  // Mock dropdown suggestions
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value;
    setInputValue(input);

    if (input) {
      // Add input to dropdownOptions if it doesn't already exist
      setDropdownOptions((prevOptions) => {
        const updatedOptions = prevOptions.includes(input)
          ? prevOptions
          : [...prevOptions, input];
        return updatedOptions.filter((item) => item.includes(input));
      });
    } else {
      setDropdownOptions([]);
    }
  };

  return (
    <div className="py-4">
      {/* Label */}
      <label className="mb-2 block text-sm text-gray-400">Selected Dates</label>

      {/* Container */}
      <div className="flex flex-wrap items-center gap-2 rounded-md border border-red-500 bg-gray-800 p-2">
        {selectedDates.map((date) => (
          <div
            key={date}
            className="flex items-center space-x-2 rounded-md bg-red-500 px-3 py-1 text-white"
          >
            <span className="text-sm">{date}</span>
            <button
              className="hover:text-gray-300 focus:outline-none"
              onClick={() => removeDate(date)}
            >
              ✕
            </button>
          </div>
        ))}
        {/* Input Field */}
        <input
          type="date"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={addDate}
          placeholder="Add a date..."
          className="flex-1 border-none bg-gray-700 p-1 text-gray-200 focus:outline-none"
        />
      </div>

      {/* Dropdown */}
      {dropdownOptions.length > 0 ? (
        <div className="mt-2 max-h-32 overflow-auto rounded-md bg-gray-800 text-gray-200 shadow-lg">
          {dropdownOptions.map((option, index) => (
            <div
              key={index}
              className="cursor-pointer p-2 hover:bg-gray-700"
              onClick={() => {
                setSelectedDates([...selectedDates, option]);
                setInputValue("");
                setDropdownOptions([]);
              }}
            >
              {option}
            </div>
          ))}
        </div>
      ) : (
        inputValue && <div className="mt-2 text-gray-400">No results</div>
      )}
    </div>
  );
};

export default SelectableDates;
