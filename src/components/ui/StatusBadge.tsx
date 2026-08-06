import React from 'react';
import { motion } from 'framer-motion';

type StatusType = 'success' | 'warning' | 'error' | 'info' | 'purple' | 'default' | 'WORKING' | 'WEEKOFF' | 'CUTOFF' | string;

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  dot?: boolean;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const statusStyles: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  success: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    dot: 'bg-emerald-500',
  },
  warning: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    dot: 'bg-amber-500',
  },
  error: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dot: 'bg-red-500',
  },
  info: {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    dot: 'bg-blue-500',
  },
  purple: {
    bg: 'bg-purple-50',
    text: 'text-purple-700',
    border: 'border-purple-200',
    dot: 'bg-purple-500',
  },
  default: {
    bg: 'bg-neutral-100',
    text: 'text-neutral-600',
    border: 'border-neutral-300',
    dot: 'bg-neutral-500',
  },
  WORKING: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    dot: 'bg-emerald-500',
  },
  WEEKOFF: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    dot: 'bg-red-500',
  },
  CUTOFF: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
    dot: 'bg-amber-500',
  },
};

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-xs',
  lg: 'px-4 py-1.5 text-sm',
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  dot = true,
  size = 'md',
  animated = true,
}) => {
  const styles = statusStyles[status] ?? statusStyles['default'];

  return (
    <motion.span
      className={`inline-flex items-center gap-1.5 ${sizes[size]} rounded-full font-semibold uppercase tracking-wider ${styles.bg} ${styles.text} border ${styles.border}`}
      initial={animated ? { opacity: 0, scale: 0.9 } : undefined}
      animate={animated ? { opacity: 1, scale: 1 } : undefined}
      transition={{ duration: 0.2 }}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${styles.dot}`} />
      )}
      {label}
    </motion.span>
  );
};

export default StatusBadge;
