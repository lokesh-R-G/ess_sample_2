import React from 'react';
import Chart from 'react-apexcharts';

interface BarChartProps {
  data: { name: string; data: number[] }[];
  categories: string[];
  horizontal?: boolean;
  height?: number;
  stacked?: boolean;
}

export const BarChart: React.FC<BarChartProps> = ({
  data,
  categories,
  horizontal = false,
  height = 350,
  stacked = false,
}) => {
  const options = {
    chart: {
      type: 'bar' as const,
      toolbar: { show: false },
      fontFamily: 'Inter, sans-serif',
      background: 'transparent',
      stacked,
    },
    plotOptions: {
      bar: {
        horizontal,
        borderRadius: 4,
        borderRadiusApplication: 'end' as const,
        columnWidth: horizontal ? '70%' : '45%',
        dataLabels: {
          position: 'top' as const,
        },
      },
    },
    dataLabels: {
      enabled: !horizontal,
      formatter: (val: number) => val.toLocaleString(),
      style: {
        fontSize: '10px',
        fontFamily: 'Inter, sans-serif',
        fontWeight: 600,
        colors: ['#00924C'],
      },
      offsetY: -20,
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
        formatter: (val: number) => val.toLocaleString(),
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

  return <Chart options={options} series={data} type="bar" height={height} />;
};

export default BarChart;
