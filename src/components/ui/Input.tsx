import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  icon?: LucideIcon;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, icon: Icon, error, helperText, className = '', ...props }, ref) => {
    return (
      <motion.div
        className="space-y-1.5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {label && (
          <label className="block text-sm font-medium text-neutral-700">{label}</label>
        )}
        <div className="relative">
          {Icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
              <Icon className="w-5 h-5" />
            </div>
          )}
          <input
            ref={ref}
            className={`
              w-full px-4 py-3 rounded-lg
              bg-white
              border border-neutral-300
              text-neutral-900 placeholder-neutral-400
              focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
              transition-all duration-200
              ${Icon ? 'pl-11' : ''}
              ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
              ${className}
            `}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-red-600">{error}</p>}
        {helperText && !error && <p className="text-xs text-neutral-500">{helperText}</p>}
      </motion.div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
