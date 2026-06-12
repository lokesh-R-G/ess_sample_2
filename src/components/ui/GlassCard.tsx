import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface GlassCardProps extends HTMLMotionProps<'div'> {
  variant?: 'default' | 'bordered' | 'elevated';
  hover?: boolean;
  children: React.ReactNode;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  variant = 'default',
  hover = true,
  children,
  className = '',
  ...props
}) => {
  const baseStyles = 'rounded-xl bg-white';

  const variants = {
    default: 'border border-neutral-200 shadow-card',
    bordered: 'border-2 border-primary-500 shadow-card',
    elevated: 'border border-neutral-200 shadow-lg',
  };

  return (
    <motion.div
      className={`${baseStyles} ${variants[variant]} ${hover ? 'card-hover' : ''} ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
