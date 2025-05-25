"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type CronExpression = {
  next_execution: string;
  next_execution_full: string;
  explanation: string;
};

type Integration = {
  id: string;
  integration_name: string;
  cron_expression: CronExpression[];
  is_running: boolean;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
};

type Props = {
  data: Integration[];
};

function getHoursUntil(dateStr: string): number {
  const now = new Date();
  const future = new Date(dateStr);
  const diffMs = future.getTime() - now.getTime();
  return Math.max(0, Math.round(diffMs / (1000 * 60 * 60))); // hours
}

export const CronScheduleChart = ({ data }: Props) => {
  const chartData = data.map((item) => {
    const nextRunStr = item.cron_expression[0].next_execution_full;
    const hoursUntilRun = getHoursUntil(nextRunStr);

    return {
      name:
        item.integration_name.length > 20
          ? item.integration_name.slice(0, 20) + "..."
          : item.integration_name,
      hoursUntilRun,
    };
  });

  return (
    <div className="">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {data.map((integration) => (
          <Card key={integration.id} className="rounded-xl h-auto shadow-sm border">
            <CardContent className="p-4 space-y-2">
              <h3 className="text-base font-semibold truncate" title={integration.integration_name}>
                {integration.integration_name}
              </h3>
              <p className="text-sm text-muted-foreground">
                {integration.cron_expression[0].explanation}
              </p>
              <p className="text-xs text-muted-foreground">
                Next run:{" "}
                <strong>
                  {integration.cron_expression[0].next_execution_full}
                </strong>
              </p>
              <div className="flex gap-2">
                {integration.is_enabled && <Badge>Enabled</Badge>}
                {integration.is_running && (
                  <Badge variant="secondary">Running</Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
