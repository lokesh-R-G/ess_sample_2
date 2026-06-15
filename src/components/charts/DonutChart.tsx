import React from 'react';
import Chart from 'react-apexcharts';

interface DonutChartProps {
  labels: string[];
  series: number[];
  colors?: string[];
  height?: number;
}

export const DonutChart: React.FC<DonutChartProps> = ({
  labels,
  series,
  colors = ['#00924C', '#3b82f6', '#9333ea', '#f59e0b', '#ef4444'],
  height = 300,
}) => {
  if (!series || series.length === 0 || !labels || labels.length === 0) return null;
  const options = {
    chart: {
      type: 'donut' as const,
      fontFamily: 'Inter, sans-serif',
      background: 'transparent',
    },
    labels,
    colors,
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${val.toFixed(1)}%`,
      style: {
        fontSize: '12px',
        fontFamily: 'Inter, sans-serif',
        fontWeight: 600,
      },
      dropShadow: { enabled: false },
    },
    legend: {
      position: 'bottom' as const,
      labels: { colors: '#525252' },
      itemMargin: { horizontal: 10, vertical: 5 },
    },
    stroke: { show: false },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            name: {
              show: true,
              fontSize: '14px',
              fontWeight: 600,
              color: '#171717',
            },
            value: {
              show: true,
              fontSize: '24px',
              fontWeight: 700,
              color: '#171717',
              formatter: (val: string) => val,
            },
            total: {
              show: true,
              label: 'Total',
              color: '#737373',
              formatter: (w: any) => w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0),
            },
          },
        },
      },
    },
    tooltip: {
      theme: 'light' as const,
      backgroundColor: '#FFFFFF',
      borderColor: '#e5e5e5',
      style: { fontSize: '12px' },
    },
  };

  return <Chart options={options} series={series} type="donut" height={height} />;
};

export default DonutChart;
