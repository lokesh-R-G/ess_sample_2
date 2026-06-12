import React from 'react';
import Chart from 'react-apexcharts';

interface AreaChartProps {
  data: { name: string; data: number[] }[];
  categories: string[];
  title?: string;
  height?: number;
}

export const AreaChart: React.FC<AreaChartProps> = ({
  data,
  categories,
  height = 350,
}) => {
  const options = {
    chart: {
      type: 'area' as const,
      toolbar: { show: false },
      fontFamily: 'Inter, sans-serif',
      background: 'transparent',
    },
    theme: { mode: 'light' as const },
    dataLabels: { enabled: false },
    stroke: {
      curve: 'smooth' as const,
      width: 2,
    },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0.1,
        stops: [0, 90, 100],
      },
    },
    colors: ['#00924C', '#3b82f6', '#9333ea'],
    xaxis: {
      categories,
      labels: {
        style: { colors: '#737373', fontSize: '12px' },
      },
      axisBorder: { show: true, color: '#e5e5e5' },
      axisTicks: { show: false },
    },
    yaxis: {
      labels: {
        style: { colors: '#737373', fontSize: '12px' },
      },
    },
    grid: {
      borderColor: '#e5e5e5',
      strokeDashArray: 4,
    },
    tooltip: {
      theme: 'light' as const,
      backgroundColor: '#FFFFFF',
      borderColor: '#e5e5e5',
      style: { fontSize: '12px' },
    },
    legend: {
      position: 'top' as const,
      horizontalAlign: 'right' as const,
      labels: { colors: '#525252' },
    },
  };

  return (
    <Chart options={options} series={data} type="area" height={height} />
  );
};

export default AreaChart;
