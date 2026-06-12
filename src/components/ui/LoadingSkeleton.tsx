import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
  variant?: 'card' | 'text' | 'circle' | 'table' | 'chart';
  count?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'card',
  count = 1,
  className = '',
}) => {
  const baseAnimation = {
    animate: { opacity: [0.5, 1, 0.5] },
    transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
  };

  const skeletonVariants = {
    card: (
      <motion.div
        className={`rounded-xl bg-white/5 p-4 space-y-3 ${className}`}
        {...baseAnimation}
      >
        <motion.div className="h-32 w-full rounded-lg bg-white/10" />
        <motion.div className="h-4 w-3/4 rounded bg-white/10" />
        <motion.div className="h-4 w-1/2 rounded bg-white/10" />
      </motion.div>
    ),
    text: (
      <motion.div
        className={`space-y-2 ${className}`}
        {...baseAnimation}
      >
        <motion.div className="h-4 w-full rounded bg-white/10" />
        <motion.div className="h-4 w-5/6 rounded bg-white/10" />
        <motion.div className="h-4 w-4/6 rounded bg-white/10" />
      </motion.div>
    ),
    circle: (
      <motion.div
        className={`w-12 h-12 rounded-full bg-white/10 ${className}`}
        {...baseAnimation}
      />
    ),
    table: (
      <motion.div
        className={`rounded-xl bg-white/5 overflow-hidden ${className}`}
        {...baseAnimation}
      >
        <div className="h-10 bg-primary-500/10" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-14 border-t border-white/5 flex items-center gap-4 px-4">
            <motion.div className="h-4 w-8 rounded bg-white/10" />
            <motion.div className="h-4 w-1/4 rounded bg-white/10" />
            <motion.div className="h-4 w-1/3 rounded bg-white/10" />
            <motion.div className="h-4 w-1/5 rounded bg-white/10" />
          </div>
        ))}
      </motion.div>
    ),
    chart: (
      <motion.div
        className={`rounded-xl bg-white/5 p-4 ${className}`}
        {...baseAnimation}
      >
        <motion.div className="h-4 w-1/4 rounded bg-white/10 mb-4" />
        <motion.div className="h-48 w-full rounded-lg bg-white/10" />
      </motion.div>
    ),
  };

  return (
    <>
      {[...Array(count)].map((_, index) => (
        <React.Fragment key={index}>{skeletonVariants[variant]}</React.Fragment>
      ))}
    </>
  );
};

export default LoadingSkeleton;
