import React, { forwardRef, useState } from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, Eye, EyeOff } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  icon?: LucideIcon;
  error?: string;
  helperText?: string;
  isPassword?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, icon: Icon, error, helperText, isPassword = false, type = 'text', className = '', ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const resolvedType = isPassword ? (showPassword ? 'text' : 'password') : type;

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
            type={resolvedType}
            className={`
              w-full px-4 py-3 rounded-lg
              bg-white
              border border-neutral-300
              text-neutral-900 placeholder-neutral-400
              focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
              transition-all duration-200
              ${Icon ? 'pl-11' : ''}
              ${isPassword ? 'pr-11' : ''}
              ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
              ${className}
            `}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 focus:outline-none"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          )}
        </div>
        {error && <p className="text-xs text-red-600">{error}</p>}
        {helperText && !error && <p className="text-xs text-neutral-500">{helperText}</p>}
      </motion.div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
