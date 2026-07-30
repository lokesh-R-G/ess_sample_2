import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { Search, ChevronDown, Check } from 'lucide-react';
import { api } from '../../lib/api';

interface ESSLMachineLookupProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  placeholder?: string;
  error?: string;
  required?: boolean;
}

export const ESSLMachineLookup: React.FC<ESSLMachineLookupProps> = ({
  value,
  onChange,
  label,
  placeholder = 'Search eSSL Machine...',
  error,
  required
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [dropdownStyle, setDropdownStyle] = useState<React.CSSProperties>({});
  
  const wrapperRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Initial load if a value already exists (e.g. editing a Branch)
  useEffect(() => {
    if (value && !selectedItem) {
      const fetchInitial = async () => {
        try {
          const res: any = await api.get(`/v2/organization/search/?entity=ESSLMachine&limit=100`);
          const items = res.data || [];
          // The API might return `id` or `_id`, so we check both safely
          const found = items.find((i: any) => (i.id || i._id) === value);
          if (found) {
            setSelectedItem(found);
            setSearchTerm(found.serialNumber);
          }
        } catch (e) {
          console.error('Error fetching initial eSSL Machine data', e);
        }
      };
      fetchInitial();
    }
  }, [value, selectedItem]);

  // Handle clicking outside to close the dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (
        wrapperRef.current && !wrapperRef.current.contains(target) &&
        (!dropdownRef.current || !dropdownRef.current.contains(target))
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Dynamic Positioning to avoid overflow-hidden clipping inside modals
  const updatePosition = () => {
    if (wrapperRef.current) {
      const rect = wrapperRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      const dropdownHeight = 250; 
      
      const style: React.CSSProperties = {
        position: 'fixed',
        left: rect.left,
        width: rect.width,
        zIndex: 9999, // Safely float above modal boundaries
      };

      // Smart flip: open upwards if near the bottom of the viewport
      if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
        style.bottom = window.innerHeight - rect.top + 4;
        style.transformOrigin = 'bottom';
      } else {
        style.top = rect.bottom + 4;
        style.transformOrigin = 'top';
      }
      setDropdownStyle(style);
    }
  };

  // Recompute positioning during scrolls or resizes
  useLayoutEffect(() => {
    if (isOpen) {
      updatePosition();
      window.addEventListener('scroll', updatePosition, true); // capture phase for modal inner-scrolling
      window.addEventListener('resize', updatePosition);
    }
    return () => {
      window.removeEventListener('scroll', updatePosition, true);
      window.removeEventListener('resize', updatePosition);
    };
  }, [isOpen]);

  // Debounced search
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (isOpen) {
        setLoading(true);
        try {
          const res: any = await api.get(`/v2/organization/search/?entity=ESSLMachine&search=${searchTerm}&limit=50`);
          setResults(res.data || []);
        } catch (e) {
          console.error('Error searching eSSL Machines', e);
        } finally {
          setLoading(false);
        }
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, isOpen]);

  const handleSelect = (item: any) => {
    setSelectedItem(item);
    setSearchTerm(item.serialNumber);
    // Store either id or _id depending on backend format
    onChange(item.id || item._id);
    setIsOpen(false);
  };

  const handleInputClick = () => {
    setIsOpen(true);
    // Temporarily clear input so they can see all options when clicking again
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
          value={isOpen ? searchTerm : (selectedItem?.serialNumber || '')}
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

      {isOpen && createPortal(
        <motion.div
          ref={dropdownRef}
          initial={{ opacity: 0, scaleY: 0.95 }}
          animate={{ opacity: 1, scaleY: 1 }}
          transition={{ duration: 0.15 }}
          className="bg-white border border-neutral-200 rounded-lg shadow-xl overflow-hidden"
          style={{ ...dropdownStyle, maxHeight: '250px' }}
        >
          <div className="overflow-y-auto max-h-[250px]">
            {loading ? (
              <div className="p-4 text-center text-sm text-neutral-500">Loading...</div>
            ) : results.length > 0 ? (
              <ul className="py-1">
                {results.map((item) => {
                  const itemId = item.id || item._id;
                  const isSelected = value === itemId;

                  return (
                    <li
                      key={itemId}
                      onClick={() => handleSelect(item)}
                      className={`
                        px-4 py-2 cursor-pointer flex justify-between items-center text-sm
                        hover:bg-primary-50
                        ${isSelected ? 'bg-primary-50 text-primary-900' : 'text-neutral-700'}
                      `}
                    >
                      <div className="flex flex-col">
                        <span className={isSelected ? 'font-medium' : ''}>{item.serialNumber}</span>
                        <span className="text-xs text-neutral-500 mt-0.5">
                          {item.ipAddress} &bull; {item.status || 'Unknown'}
                        </span>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-primary-600 flex-shrink-0 ml-3" />}
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="p-4 text-center text-sm text-neutral-500">No matching devices found</div>
            )}
          </div>
        </motion.div>,
        document.body
      )}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
};

export default ESSLMachineLookup;
