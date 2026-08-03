import React, { useState } from 'react';
import { Settings, Shield, Activity, Receipt, SlidersHorizontal } from 'lucide-react';
import PayrollSettingsTab from './tabs/PayrollSettingsTab';
import PFRulesTab from './tabs/PFRulesTab';
import ESIRulesTab from './tabs/ESIRulesTab';
import PTRulesTab from './tabs/PTRulesTab';
import ComponentBehaviorTab from './tabs/ComponentBehaviorTab';

export default function AdminPayrollRules() {
  const [activeTab, setActiveTab] = useState('settings');

  const tabs = [
    { id: 'settings', label: 'General Settings', icon: Settings },
    { id: 'pf', label: 'PF Rules', icon: Shield },
    { id: 'esi', label: 'ESI Rules', icon: Activity },
    { id: 'pt', label: 'PT Rules', icon: Receipt },
    { id: 'components', label: 'Component Behaviors', icon: SlidersHorizontal },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Payroll Rules Engine</h1>
          <p className="text-neutral-500 mt-1">Configure global statutory rules and payroll settings</p>
        </div>
      </div>

      {/* Tabs Header */}
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

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'settings' && <PayrollSettingsTab />}
        {activeTab === 'pf' && <PFRulesTab />}
        {activeTab === 'esi' && <ESIRulesTab />}
        {activeTab === 'pt' && <PTRulesTab />}
        {activeTab === 'components' && <ComponentBehaviorTab />}
      </div>
    </div>
  );
}
