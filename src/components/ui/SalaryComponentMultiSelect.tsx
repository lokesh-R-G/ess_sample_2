import React, { useState, useEffect } from 'react';
import { Check, ChevronDown, ChevronUp, Search } from 'lucide-react';
import { api } from '../../lib/api';

interface SalaryComponent {
  _id: string;
  name: string;
  componentType?: string;
  calculationMethod?: string;
}

interface SalaryComponentMultiSelectProps {
  value: string[];                     // array of selected component _id strings
  onChange: (ids: string[]) => void;
  label?: string;
  required?: boolean;
  error?: string;
}

export const SalaryComponentMultiSelect: React.FC<SalaryComponentMultiSelectProps> = ({
  value = [],
  onChange,
  label = 'Salary Components',
  required,
  error,
}) => {
  const [components, setComponents] = useState<SalaryComponent[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        const res: any = await api.get('/v2/organization/salary-components/?limit=500');
        const items: SalaryComponent[] = (res.data?.data || res.data || []).map((c: any) => ({
          _id: c._id || c.id,
          name: c.name,
          componentType: c.componentType,
          calculationMethod: c.calculationMethod,
        }));
        setComponents(items);
      } catch (e) {
        console.error('Error loading salary components', e);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const filtered = components.filter(c =>
    c.name?.toLowerCase().includes(search.toLowerCase())
  );

  const selectedNames = components
    .filter(c => value.includes(c._id))
    .map(c => c.name);

  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter(v => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <div className="space-y-1.5">
      {label && (
        <label className="block text-sm font-medium text-neutral-700">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      {/* Summary bar – shows selected count and toggles panel */}
      <button
        type="button"
        onClick={() => setExpanded(e => !e)}
        className={`
          w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm
          bg-white border transition-all duration-200 text-left
          ${expanded ? 'border-primary-500 ring-2 ring-primary-500/20' : 'border-neutral-300'}
          ${error ? 'border-red-500' : ''}
        `}
      >
        <span className={value.length === 0 ? 'text-neutral-400' : 'text-neutral-900'}>
          {value.length === 0
            ? 'Select salary components…'
            : `${value.length} component${value.length > 1 ? 's' : ''} selected`}
        </span>
        {expanded ? <ChevronUp className="w-4 h-4 text-neutral-400" /> : <ChevronDown className="w-4 h-4 text-neutral-400" />}
      </button>

      {/* Selected chips */}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {components
            .filter(c => value.includes(c._id))
            .map(c => (
              <span
                key={c._id}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-800 border border-primary-200"
              >
                <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${c.componentType === 'Deduction' ? 'bg-red-500' : 'bg-emerald-500'}`} />
                {c.name}
                <button
                  type="button"
                  onClick={() => toggle(c._id)}
                  className="ml-0.5 text-primary-600 hover:text-red-600 transition-colors"
                  aria-label={`Remove ${c.name}`}
                >
                  ×
                </button>
              </span>
            ))}
        </div>
      )}

      {/* Expandable checklist */}
      {expanded && (
        <div className="border border-neutral-200 rounded-lg bg-white shadow-lg overflow-hidden">
          {/* Search input */}
          <div className="p-2 border-b border-neutral-100">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-neutral-400" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Filter components…"
                className="w-full pl-8 pr-3 py-1.5 text-sm rounded-md border border-neutral-200 focus:outline-none focus:border-primary-400"
                autoFocus
              />
            </div>
          </div>

          {/* List */}
          <div className="overflow-y-auto max-h-56">
            {loading ? (
              <div className="p-4 text-center text-sm text-neutral-500">Loading components…</div>
            ) : filtered.length === 0 ? (
              <div className="p-4 text-center text-sm text-neutral-500">No matching components</div>
            ) : (
              <>
                {/* Group: Earnings */}
                {filtered.some(c => c.componentType === 'Earning') && (
                  <div>
                    <div className="px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700 bg-emerald-50">Earnings</div>
                    {filtered.filter(c => c.componentType === 'Earning').map(c => (
                      <ComponentRow key={c._id} component={c} selected={value.includes(c._id)} onToggle={() => toggle(c._id)} />
                    ))}
                  </div>
                )}
                {/* Group: Deductions */}
                {filtered.some(c => c.componentType === 'Deduction') && (
                  <div>
                    <div className="px-3 py-1 text-xs font-semibold uppercase tracking-wide text-red-700 bg-red-50">Deductions</div>
                    {filtered.filter(c => c.componentType === 'Deduction').map(c => (
                      <ComponentRow key={c._id} component={c} selected={value.includes(c._id)} onToggle={() => toggle(c._id)} />
                    ))}
                  </div>
                )}
                {/* Ungrouped */}
                {filtered.filter(c => !c.componentType).map(c => (
                  <ComponentRow key={c._id} component={c} selected={value.includes(c._id)} onToggle={() => toggle(c._id)} />
                ))}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="px-3 py-2 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-500">
            <span>{value.length} selected of {components.length}</span>
            {value.length > 0 && (
              <button type="button" onClick={() => onChange([])} className="text-red-500 hover:underline">
                Clear all
              </button>
            )}
          </div>
        </div>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
};

const ComponentRow: React.FC<{ component: SalaryComponent; selected: boolean; onToggle: () => void }> = ({
  component, selected, onToggle,
}) => (
  <div
    onClick={onToggle}
    className={`
      flex items-center justify-between px-3 py-2 cursor-pointer text-sm transition-colors
      hover:bg-neutral-50
      ${selected ? 'bg-primary-50/60' : ''}
    `}
  >
    <div className="flex items-center gap-2.5">
      <div className={`w-4 h-4 rounded flex items-center justify-center border transition-colors flex-shrink-0
        ${selected ? 'bg-primary-600 border-primary-600' : 'border-neutral-300 bg-white'}`}
      >
        {selected && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
      </div>
      <span className={selected ? 'font-medium text-primary-900' : 'text-neutral-700'}>{component.name}</span>
    </div>
    <span className={`text-xs px-1.5 py-0.5 rounded-full ${
      component.componentType === 'Deduction'
        ? 'bg-red-50 text-red-700'
        : component.componentType === 'Earning'
        ? 'bg-emerald-50 text-emerald-700'
        : 'bg-neutral-100 text-neutral-500'
    }`}>
      {component.calculationMethod || component.componentType || '—'}
    </span>
  </div>
);

export default SalaryComponentMultiSelect;
