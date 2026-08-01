import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Check } from 'lucide-react';
import { api } from '../../lib/api';

interface LookupSelectProps {
  entity: string;
  value: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  error?: string;
  required?: boolean;
  labelField?: string;
  valueField?: string;
}

export const LookupSelect: React.FC<LookupSelectProps> = ({
  entity,
  value,
  onChange,
  label,
  placeholder = 'Search...',
  error,
  required,
  labelField = 'name',
  valueField = '_id'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Initial load of the selected item if a value exists
  useEffect(() => {
    if (value && !selectedItem) {
      // We do a direct search to find the item
      const fetchInitial = async () => {
        try {
          const res: any = await api.get(`/v2/organization/search/?entity=${entity}&limit=100`);
          const items = res?.data || res || [];
          const found = items.find((i: any) => i[valueField] === value);
          if (found) {
            setSelectedItem(found);
            setSearchTerm(found[labelField] || found[valueField]);
          }
        } catch (e) {
          console.error('Error fetching initial lookup data', e);
        }
      };
      fetchInitial();
    }
  }, [value, entity]);

  // Handle clicking outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (isOpen) {
        setLoading(true);
        try {
          const res: any = await api.get(`/v2/organization/search/?entity=${entity}&search=${searchTerm}&limit=50`);
          setResults(res?.data || res || []);
        } catch (e) {
          console.error('Error searching', e);
        } finally {
          setLoading(false);
        }
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, isOpen, entity]);

  const handleSelect = (item: any) => {
    setSelectedItem(item);
    setSearchTerm(item[labelField] || item[valueField]);
    onChange(item[valueField]);
    setIsOpen(false);
  };

  const handleInputClick = () => {
    setIsOpen(true);
    // If we already have a selected item, clear search term temporarily so they see all results
    if (selectedItem) {
      setSearchTerm('');
    }
  };

  return (
    <div className="space-y-1.5" ref={wrapperRef}>
      {label && (
        <label className="block text-sm font-medium text-neutral-700">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          className={`
            w-full px-4 py-3 pl-9 pr-10 rounded-lg outline-none
            bg-white border border-neutral-300 text-neutral-900
            focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20
            transition-all duration-200
            ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
          `}
          placeholder={placeholder}
          value={isOpen ? searchTerm : (selectedItem?.[labelField] || '')}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onClick={handleInputClick}
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-400">
          <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-1 bg-white border border-neutral-200 rounded-lg shadow-xl overflow-hidden"
            style={{ maxHeight: '250px' }}
          >
            <div className="overflow-y-auto max-h-[250px]">
              {loading ? (
                <div className="p-4 text-center text-sm text-neutral-500">Loading...</div>
              ) : results.length > 0 ? (
                <ul className="py-1">
                  {results.map((item) => (
                    <li
                      key={item[valueField]}
                      onClick={() => handleSelect(item)}
                      className={`
                        px-4 py-2 cursor-pointer flex justify-between items-center text-sm
                        hover:bg-primary-50
                        ${value === item[valueField] ? 'bg-primary-50 text-primary-900 font-medium' : 'text-neutral-700'}
                      `}
                    >
                      <span>{item[labelField] || item[valueField]}</span>
                      {value === item[valueField] && <Check className="w-4 h-4 text-primary-600" />}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-4 text-center text-sm text-neutral-500">No results found</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
};

export default LookupSelect;
