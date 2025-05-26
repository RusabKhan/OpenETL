"use client";

import { LogsConfig } from "../types/integration";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import Spinner from "../Spinner";
import { IconRefresh } from "@tabler/icons-react";

interface LogPanelInterface {
  title: string;
  logsData: LogsConfig | undefined;
  isLoading: boolean;
  nextPage: () => void;
  previousPage: () => void;
  reload: (cache: boolean) => void;
}

const LogPanel = ({
  title,
  logsData,
  isLoading,
  nextPage,
  previousPage,
  reload,
}: LogPanelInterface) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          <Button variant="outline" size="sm" onClick={() => reload(false)}>
            <IconRefresh /> Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Logs Section */}
        <div className="h-[50vh] overflow-y-auto rounded-lg bg-muted p-4">
          {logsData && logsData.logs.length > 0 ? (
            logsData.logs.map((log, index) => (
              <div
                key={index}
                className="mb-2 break-all rounded-md bg-secondary p-2 text-xs text-secondary-foreground"
              >
                {log}
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No logs available.</p>
          )}
        </div>

        {/* Pagination */}
        <nav
          className="flex flex-wrap items-center justify-between pt-4"
          aria-label="Table navigation"
        >
          <div className="text-sm text-muted-foreground">
            Total Pages:{" "}
            <span className="font-semibold text-foreground">
              {logsData?.total_pages || 0}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={previousPage}
              disabled={logsData?.page === 1}
            >
              Previous
            </Button>
            <Button variant="outline" size="sm" disabled>
              {logsData?.page || 1}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={nextPage}
              disabled={
                logsData?.page === logsData?.total_pages ||
                logsData?.total_pages === 0
              }
            >
              Next
            </Button>
          </div>
        </nav>

        {/* Loading Spinner */}
        {isLoading && <Spinner visible={isLoading} />}
      </CardContent>
    </Card>
  );
};

export default LogPanel;
