import React, { useState } from 'react';
import { Shield, Activity, Receipt } from 'lucide-react';
import PFRulesTab from './PFRulesTab';
import ESIRulesTab from './ESIRulesTab';
import PTRulesTab from './PTRulesTab';

export default function PayrollRulesTab() {
  const [activeTab, setActiveTab] = useState('pf');

  const tabs = [
    { id: 'pf', label: 'PF Rules', icon: Shield },
    { id: 'esi', label: 'ESI Rules', icon: Activity },
    { id: 'pt', label: 'PT Rules', icon: Receipt },
  ];

  return (
    <div className="space-y-6 bg-white p-6 rounded-2xl border border-neutral-200">
      <div className="flex space-x-1 border-b border-neutral-200">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors
                ${isActive 
                  ? 'border-brand-500 text-brand-600 bg-brand-50/50 rounded-t-lg' 
                  : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'}
              `}
            >
              <Icon className={`w-4 h-4 mr-2 ${isActive ? 'text-brand-500' : 'text-neutral-400'}`} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="mt-6">
        {activeTab === 'pf' && <PFRulesTab />}
        {activeTab === 'esi' && <ESIRulesTab />}
        {activeTab === 'pt' && <PTRulesTab />}
      </div>
    </div>
  );
}
