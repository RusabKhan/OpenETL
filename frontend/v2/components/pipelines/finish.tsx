"use client";

import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { IntegrationConfig } from "../types/integration";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import SelectableDates from "../SelectableDates";

const frequencyOptions = ["Weekly", "Monthly", "Daily", "Weekends", "Weekday"];

const FinishTab: React.FC<{
  integration: IntegrationConfig;
  setIntegration: Dispatch<SetStateAction<IntegrationConfig>>;
}> = ({ integration, setIntegration }) => {
  const [scheduleType, setScheduleType] = useState("frequency");

  useEffect(() => {
    setIntegration((prev) => ({
      ...prev,
      integration_name: `${integration.source_schema}_${integration.source_table}_to_${integration.target_schema}_${integration.target_table}`,
    }));
  }, []);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Finish</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Integration Name */}
            <div>
              <Label>Enter Unique Integration Name</Label>
              <Input
                value={integration.integration_name}
                onChange={(e) =>
                  setIntegration((prev) => ({
                    ...prev,
                    integration_name: e.target.value,
                  }))
                }
                placeholder="Enter integration name"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                {/* Schedule Type */}
                <div className="mb-4">
                  <Label>Select Schedule Type</Label>
                  <RadioGroup
                    value={scheduleType}
                    onValueChange={(value) => setScheduleType(value)}
                    className="flex flex-col gap-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="frequency" id="frequency" />
                      <Label htmlFor="frequency">Frequency</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem
                        value="selectedDates"
                        id="selectedDates"
                      />
                      <Label htmlFor="selectedDates">Selected Dates</Label>
                    </div>
                  </RadioGroup>
                </div>

                {/* Frequency */}
                {scheduleType !== "selectedDates" && (
                  <div className="mb-4">
                    <Label>Select Frequency</Label>
                    <Select
                      onValueChange={(value) =>
                        setIntegration((prev) => ({
                          ...prev,
                          frequency: value,
                        }))
                      }
                      disabled={scheduleType === "selectedDates"}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select Frequency" />
                      </SelectTrigger>
                      <SelectContent>
                        {frequencyOptions.map((option, i) => (
                          <SelectItem key={i} value={option}>
                            {option}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Integration Type */}
                <div className="mb-4">
                  <Label>Select Integration Type</Label>
                  <RadioGroup
                    value={integration.integration_type}
                    className="flex gap-4"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem
                        value={integration.integration_type}
                        id="integrationType"
                      />
                      <Label htmlFor="integrationType">
                        {integration.integration_type.replace("_", " ")}
                      </Label>
                    </div>
                  </RadioGroup>
                </div>
              </div>
              <div>
                {/* Schedule Time */}
                <div className="mb-4">
                  <Label>Schedule Time</Label>
                  <Input
                    type="time"
                    value={integration.schedule_time}
                    onChange={(e) =>
                      setIntegration((prev) => ({
                        ...prev,
                        schedule_time: e.target.value,
                      }))
                    }
                  />
                  <p className="text-xs mt-1">
                    Enter the time according to the time at top.
                  </p>
                </div>

                {/* Selectable Dates */}
                {scheduleType === "selectedDates" && (
                  <div>
                    <SelectableDates
                      integration={integration}
                      setIntegration={setIntegration}
                    />
                  </div>
                )}

                {/* Batch Size */}
                <div>
                  <Label>Batch Size</Label>
                  <Input
                    type="number"
                    value={integration.batch_size}
                    onChange={(e) =>
                      setIntegration((prev) => ({
                        ...prev,
                        batch_size: parseInt(e.target.value),
                      }))
                    }
                    placeholder="Enter batch size"
                  />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FinishTab;
