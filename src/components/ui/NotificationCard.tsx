import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

interface NotificationCardProps {
  title: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  time?: string;
  onClose?: () => void;
  onClick?: () => void;
}

const icons = {
  info: Info,
  success: CheckCircle,
  warning: AlertCircle,
  error: AlertCircle,
};

const typeStyles = {
  info: 'border-blue-200 bg-blue-50',
  success: 'border-emerald-200 bg-emerald-50',
  warning: 'border-amber-200 bg-amber-50',
  error: 'border-red-200 bg-red-50',
};

const iconStyles = {
  info: 'text-blue-600',
  success: 'text-emerald-600',
  warning: 'text-amber-600',
  error: 'text-red-600',
};

export const NotificationCard: React.FC<NotificationCardProps> = ({
  title,
  message,
  type = 'info',
  time,
  onClose,
  onClick,
}) => {
  const Icon = icons[type];

  return (
    <motion.div
      className={`relative rounded-lg border ${typeStyles[type]} p-3 cursor-pointer hover:shadow-sm transition-shadow`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className={`p-1.5 rounded-lg ${typeStyles[type]}`}>
          <Icon className={`w-4 h-4 ${iconStyles[type]}`} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-neutral-800">{title}</p>
          <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">{message}</p>
          {time && (
            <p className="text-xs text-neutral-400 mt-1">{time}</p>
          )}
        </div>
        {onClose && (
          <motion.button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="p-1 rounded hover:bg-white text-neutral-400 hover:text-neutral-700 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <X className="w-4 h-4" />
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};

export default NotificationCard;
