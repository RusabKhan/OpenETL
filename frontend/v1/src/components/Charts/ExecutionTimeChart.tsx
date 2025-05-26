import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";
import { DashboardIntegrationConfig } from "@/types/integration";

// Dynamically load ApexCharts (important for SSR compatibility)
const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface ExecutionTimeChartProps {
  data: DashboardIntegrationConfig[];
}

const ExecutionTimeChart: React.FC<ExecutionTimeChartProps> = ({ data }) => {
  // Filter only successful runs
  const successfulRuns = data.filter(
    (item) => item.latest_run_status === "success" && item.end_date
  );

  // Calculate execution time in seconds for each integration
  const executionData = successfulRuns.map((item) => {
    const startTime = new Date(item.start_date).getTime();
    const endTime = new Date(item.end_date!).getTime(); // Non-null assertion since we filter `end_date`
    return {
      name: item.integration_name,
      executionTime: (endTime - startTime) / 1000, // Convert milliseconds to seconds
    };
  });

  // Sort data by execution time (optional)
  executionData.sort((a, b) => b.executionTime - a.executionTime);

  // Chart options
  const options: ApexOptions = {
    chart: {
      type: "bar",
    },
    xaxis: {
      categories: executionData.map((item) => item.name.substring(0, 6) + "..."),
      title: {
        text: "Integration",
      },
    },
    yaxis: {
      title: {
        text: "Execution Time (seconds)",
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val) => `${val}s`, // Display seconds with 2 decimals
    },
    tooltip: {
      y: {
        formatter: (val) => `${val.toFixed(2)} seconds`,
      },
    },
    colors: ["#53b0ef"], // Customize bar color
  };

  // Chart series
  const series = [
    {
      name: "Execution Time",
      data: executionData.map((item) => item.executionTime),
    },
  ];

  return <Chart options={options} series={series} type="bar" />;
};

export default ExecutionTimeChart;
