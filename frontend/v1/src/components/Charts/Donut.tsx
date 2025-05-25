import dynamic from "next/dynamic";
import { ApexOptions } from "apexcharts";
import { DashboardIntegrationConfig } from "@/types/integration";

// Dynamically load ApexCharts (important for SSR compatibility)
const Chart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface DonutChartProps {
  data: DashboardIntegrationConfig[];
}

const DonutChart: React.FC<DonutChartProps> = ({ data }) => {
  // Process data to count statuses
  const statusCount = data.reduce(
    (acc, curr) => {
      acc[curr.latest_run_status] += 1;
      return acc;
    },
    { success: 0, failed: 0, running: 0 },
  );

  // Define chart options
  const options: ApexOptions = {
    chart: {
      type: "donut",
    },
    labels: ["Success", "Failed", "Running"],
    legend: {
      position: "bottom",
    },
    colors: ["#00C851", "#ff4444", "#53b0ef"],
    responsive: [
      {
        breakpoint: 768,
        options: {
          chart: {
            width: 30,
          },
        },
      },
    ],
  };

  // Define chart series
  const series = [statusCount.success, statusCount.failed, statusCount.running];

  return (
      <Chart options={options} series={series} type="donut" />
  );
};

export default DonutChart;
