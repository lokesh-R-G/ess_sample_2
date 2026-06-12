import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, LucideIcon } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  icon?: LucideIcon;
  error?: string;
  placeholder?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, icon: Icon, error, placeholder = 'Select an option', className = '', ...props }, ref) => {
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
          <select
            ref={ref}
            className={`
              w-full px-4 py-3 rounded-lg appearance-none cursor-pointer
              bg-white
              border border-neutral-300
              text-neutral-900
              focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
              transition-all duration-200
              ${Icon ? 'pl-11' : ''}
              ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
              ${className}
            `}
            {...props}
          >
            <option value="" disabled className="bg-white">
              {placeholder}
            </option>
            {options.map((option) => (
              <option key={option.value} value={option.value} className="bg-white">
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-400">
            <ChevronDown className="w-5 h-5" />
          </div>
        </div>
        {error && <p className="text-xs text-red-600">{error}</p>}
      </motion.div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
