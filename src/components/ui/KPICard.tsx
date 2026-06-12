import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: number | string;
  prefix?: string;
  suffix?: string;
  icon: LucideIcon;
  trend?: number;
  trendLabel?: string;
  color?: 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'yellow';
  delay?: number;
}

const colorSchemes = {
  green: {
    bg: 'bg-primary-50',
    border: 'border-primary-200',
    icon: 'text-primary-500',
    iconBg: 'bg-primary-100',
  },
  blue: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'text-blue-600',
    iconBg: 'bg-blue-100',
  },
  purple: {
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    icon: 'text-purple-600',
    iconBg: 'bg-purple-100',
  },
  orange: {
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: 'text-orange-600',
    iconBg: 'bg-orange-100',
  },
  red: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: 'text-red-600',
    iconBg: 'bg-red-100',
  },
  yellow: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    icon: 'text-yellow-600',
    iconBg: 'bg-yellow-100',
  },
};

const AnimatedNumber: React.FC<{ value: number; prefix?: string; suffix?: string }> = ({
  value,
  prefix = '',
  suffix = '',
}) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 30;
    const stepValue = value / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current = Math.min(Math.round(stepValue * step), value);
      setDisplayValue(current);
      if (step >= steps) {
        clearInterval(timer);
        setDisplayValue(value);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <span>
      {prefix}
      {displayValue.toLocaleString()}
      {suffix}
    </span>
  );
};

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  prefix = '',
  suffix = '',
  icon: Icon,
  trend,
  trendLabel,
  color = 'green',
  delay = 0,
}) => {
  const scheme = colorSchemes[color];
  const isNumeric = typeof value === 'number';

  return (
    <motion.div
      className={`relative rounded-xl bg-white border border-neutral-200 p-5 shadow-card`}
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, delay }}
      whileHover={{ y: -2, transition: { duration: 0.2 }, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2.5 rounded-lg ${scheme.iconBg}`}>
          <Icon className={`w-5 h-5 ${scheme.icon}`} />
        </div>
        {trend !== undefined && (
          <div
            className={`flex items-center gap-1 text-xs font-medium ${
              trend >= 0 ? 'text-success' : 'text-error'
            }`}
          >
            {trend >= 0 ? (
              <TrendingUp className="w-3.5 h-3.5" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5" />
            )}
            <span>{Math.abs(trend)}%</span>
          </div>
        )}
      </div>

      <div className="space-y-1">
        <p className="text-sm text-neutral-500 font-medium">{title}</p>
        <p className="text-2xl font-bold text-neutral-900">
          {isNumeric ? <AnimatedNumber value={value} prefix={prefix} suffix={suffix} /> : value}
        </p>
        {trendLabel && <p className="text-xs text-neutral-400">{trendLabel}</p>}
      </div>

      <div
        className={`absolute -right-4 -bottom-4 w-20 h-20 rounded-full ${scheme.bg} opacity-50`}
      />
    </motion.div>
  );
};

export default KPICard;
