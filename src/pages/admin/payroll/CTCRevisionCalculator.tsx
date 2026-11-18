import React, { useState, useEffect, useMemo } from 'react';
import { GlassCard, AnimatedButton, Input, Select } from '../../../components/ui';
import { employeeApi } from '../../../services/employeeApi';
import { organizationApi } from '../../../services/organization.api';
import {
  Calculator,
  RefreshCw,
  AlertTriangle,
  Info,
  TrendingUp,
  Percent,
  DollarSign,
  Plus,
  Trash2,
  Lock,
  UserCheck,
  CheckCircle2,
  HelpCircle,
  FileSpreadsheet
} from 'lucide-react';
import {
  CTCComponentInput,
  RevisionMethod,
  DEFAULT_EXCEL_COMPONENTS,
  calculateCTCRevision,
  formatIndianCurrency,
  formatPercentage,
  isStaticPFComponent
} from '../../../utils/ctcCalculatorEngine';

export default function CTCRevisionCalculatorPage() {
  // 1. Calculator State
  const [oldCTC, setOldCTC] = useState<number>(1400004);
  const [revisionMethod, setRevisionMethod] = useState<RevisionMethod>('TARGET_CTC');
  const [incrementPercentage, setIncrementPercentage] = useState<number>(15);
  const [targetCTC, setTargetCTC] = useState<number>(2400000);
  const [components, setComponents] = useState<CTCComponentInput[]>(DEFAULT_EXCEL_COMPONENTS);

  // New Custom Component Inline Adder
  const [newCompName, setNewCompName] = useState('');
  const [newCompAmount, setNewCompAmount] = useState<number | ''>('');
  const [newCompIsStatic, setNewCompIsStatic] = useState(false);

  // 2. Employee Prefill Integration State
  const [employees, setEmployees] = useState<any[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(false);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [loadingPrefill, setLoadingPrefill] = useState(false);
  const [prefillNotice, setPrefillNotice] = useState<string | null>(null);

  // Fetch employees for read-only prefill
  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    setLoadingEmployees(true);
    try {
      const res = await employeeApi.getEmployees();
      const list = res?.data || res || [];
      setEmployees(Array.isArray(list) ? list : []);
    } catch (err) {
      console.warn('Could not load employee directory for prefill', err);
    } finally {
      setLoadingEmployees(false);
    }
  };

  // Prefill Employee Salary Structure (Read-Only)
  const handleEmployeeSelect = async (empId: string) => {
    setSelectedEmployeeId(empId);
    setPrefillNotice(null);
    if (!empId) return;

    setLoadingPrefill(true);
    try {
      // Find employee details
      const emp = employees.find((e) => (e.id || e._id || e.employeeId) === empId);
      const codeOrId = emp?.employeeId || emp?.employeeCode || empId;

      const configRes = await employeeApi.getSalaryConfig(codeOrId);
      const config = configRes?.data || configRes || {};

      // If existing structure is present, check structure components
      let fetchedComponents: CTCComponentInput[] = [];
      let totalFetchedOld = 0;

      if (config.basicSalary) {
        const annualBasic = config.basicSalary * 12;
        fetchedComponents.push({
          id: 'basic',
          name: 'Basic',
          oldAmount: annualBasic,
          isStatic: false,
          notes: 'Prefilled from active employee salary configuration (Annualized)'
        });
        totalFetchedOld += annualBasic;
      }

      if (config.customComponents && typeof config.customComponents === 'object') {
        // Fetch component names if possible
        let compNamesMap: Record<string, string> = {};
        try {
          const allCompsRes = await organizationApi.getSalaryComponents();
          const allComps = allCompsRes?.data || allCompsRes || [];
          allComps.forEach((c: any) => {
            compNamesMap[c._id || c.id] = c.name;
          });
        } catch {
          // fallback
        }

        Object.entries(config.customComponents).forEach(([cid, monthlyAmt]) => {
          const compName = compNamesMap[cid] || `Component ${cid.substring(0, 6)}`;
          const annualAmt = Number(monthlyAmt) * 12;
          const isStatic = isStaticPFComponent(compName, cid);

          fetchedComponents.push({
            id: cid,
            name: compName,
            oldAmount: annualAmt,
            isStatic,
            notes: isStatic
              ? 'Static: fixed PF component'
              : 'Prefilled from employee configuration'
          });
          totalFetchedOld += annualAmt;
        });
      }

      if (fetchedComponents.length > 0) {
        setComponents(fetchedComponents);
        // Estimate old CTC as total annual components if not explicitly provided
        setOldCTC(totalFetchedOld);
        setPrefillNotice(`Successfully prefilled ${fetchedComponents.length} salary components for ${emp?.firstName || ''} ${emp?.lastName || ''} (${codeOrId}). Read-only mode: no actual salary records will be modified.`);
      } else {
        setPrefillNotice(`No active salary snapshot found for employee ${emp?.firstName || ''} ${emp?.lastName || ''}. You can enter values manually or use the standard reference components.`);
      }
    } catch (e: any) {
      console.warn('Salary prefill note:', e);
      setPrefillNotice('Employee salary structure not found or yet to be configured. You can enter or adjust components manually.');
    } finally {
      setLoadingPrefill(false);
    }
  };

  // Reset to reference workbook values
  const handleReset = () => {
    setOldCTC(1400004);
    setRevisionMethod('TARGET_CTC');
    setIncrementPercentage(15);
    setTargetCTC(2400000);
    setComponents(DEFAULT_EXCEL_COMPONENTS);
    setSelectedEmployeeId('');
    setPrefillNotice(null);
  };

  // Component Amount Change Handler
  const handleComponentAmountChange = (id: string, val: number) => {
    setComponents((prev) =>
      prev.map((c) => (c.id === id ? { ...c, oldAmount: Math.max(0, val) } : c))
    );
  };

  // Toggle static PF flag for a component
  const handleToggleStatic = (id: string) => {
    setComponents((prev) =>
      prev.map((c) => (c.id === id ? { ...c, isStatic: !c.isStatic } : c))
    );
  };

  // Add custom component
  const handleAddComponent = () => {
    if (!newCompName.trim()) return;
    const amount = Number(newCompAmount) || 0;
    const newId = `custom_${Date.now()}`;
    setComponents((prev) => [
      ...prev,
      {
        id: newId,
        name: newCompName.trim(),
        oldAmount: amount,
        isStatic: newCompIsStatic,
        isCustom: true,
        notes: newCompIsStatic ? 'Static component' : 'Calculated proportionally'
      }
    ]);
    setNewCompName('');
    setNewCompAmount('');
    setNewCompIsStatic(false);
  };

  // Remove component
  const handleRemoveComponent = (id: string) => {
    setComponents((prev) => prev.filter((c) => c.id !== id));
  };

  // Live Recalculation Engine Call
  const summary = useMemo(() => {
    return calculateCTCRevision({
      oldCTC,
      revisionMethod,
      incrementPercentage,
      targetCTC,
      components
    });
  }, [oldCTC, revisionMethod, incrementPercentage, targetCTC, components]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header & Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary-100 text-primary-700">
              <Calculator className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">CTC Revision Calculator</h1>
              <p className="text-sm text-neutral-500">
                Model compensation revisions, preview proportional component breakdown, and compare structures.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-lg hover:bg-neutral-50 transition shadow-sm"
          >
            <RefreshCw className="w-4 h-4 text-neutral-500" />
            Reset to Workbook Defaults
          </button>
        </div>
      </div>

      {/* Read-Only Boundary & Information Banner */}
      <div className="rounded-xl border border-primary-200 bg-primary-50/60 p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-neutral-700">
            <span className="font-semibold text-primary-900">Read-Only Calculation Sandbox: </span>
            This calculator is an analytical tool reproducing the reference workbook's calculation model. It does not modify employee CTC, write to salary tables, alter payroll historical runs, or impact statutory PF/ESI processing.
          </div>
        </div>
      </div>

      {/* Section 1: Employee Selection & Old Salary Structure Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Revision Settings & Old CTC Input */}
        <div className="space-y-6">
          {/* Employee Prefill Card */}
          <GlassCard className="p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold text-neutral-900 flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-primary-600" />
                Employee Prefill (Optional)
              </h2>
              {loadingPrefill && <span className="text-xs text-primary-600 animate-pulse font-medium">Loading...</span>}
            </div>
            <p className="text-xs text-neutral-500">
              Select an employee to prefill existing salary components, or configure amounts manually below.
            </p>
            <div>
              <select
                value={selectedEmployeeId}
                onChange={(e) => handleEmployeeSelect(e.target.value)}
                disabled={loadingEmployees}
                className="w-full text-sm rounded-lg border border-neutral-300 px-3 py-2 bg-white text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
              >
                <option value="">-- Manual Input / Select Employee --</option>
                {employees.map((emp) => {
                  const empId = emp.id || emp._id || emp.employeeId;
                  const name = `${emp.firstName || ''} ${emp.lastName || ''}`.trim() || emp.employeeCode || empId;
                  return (
                    <option key={empId} value={empId}>
                      {name} ({emp.employeeCode || emp.employeeId || 'ID: ' + empId.substring(0, 6)})
                    </option>
                  );
                })}
              </select>
            </div>
            {prefillNotice && (
              <div className="p-2.5 rounded-lg bg-neutral-50 border border-neutral-200 text-xs text-neutral-600">
                {prefillNotice}
              </div>
            )}
          </GlassCard>

          {/* Revision Parameters Card */}
          <GlassCard className="p-5 space-y-5">
            <h2 className="text-base font-semibold text-neutral-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary-600" />
              Revision Method & Inputs
            </h2>

            {/* Old Annual CTC Input */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 uppercase tracking-wider mb-1">
                Old Annual CTC (₹) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                  ₹
                </span>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={oldCTC === 0 ? '' : oldCTC}
                  onChange={(e) => setOldCTC(Math.max(0, Number(e.target.value)))}
                  placeholder="e.g. 1400004"
                  className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                Reference workbook default: ₹14,00,004
              </p>
              {oldCTC <= 0 && (
                <p className="text-xs text-red-600 mt-1 font-medium">
                  Old CTC must be greater than zero for proportional calculation.
                </p>
              )}
            </div>

            {/* Revision Mode Selector */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 uppercase tracking-wider mb-2">
                Choose Revision Method
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRevisionMethod('PERCENTAGE')}
                  className={`flex flex-col items-center justify-center p-3 rounded-lg border text-sm font-medium transition ${
                    revisionMethod === 'PERCENTAGE'
                      ? 'border-primary-500 bg-primary-50/70 text-primary-800 shadow-sm ring-1 ring-primary-400'
                      : 'border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50'
                  }`}
                >
                  <Percent className="w-4 h-4 mb-1" />
                  <span>Percentage Increment</span>
                </button>

                <button
                  type="button"
                  onClick={() => setRevisionMethod('TARGET_CTC')}
                  className={`flex flex-col items-center justify-center p-3 rounded-lg border text-sm font-medium transition ${
                    revisionMethod === 'TARGET_CTC'
                      ? 'border-primary-500 bg-primary-50/70 text-primary-800 shadow-sm ring-1 ring-primary-400'
                      : 'border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50'
                  }`}
                >
                  <DollarSign className="w-4 h-4 mb-1" />
                  <span>Target New CTC</span>
                </button>
              </div>
            </div>

            {/* Mode Specific Input */}
            {revisionMethod === 'PERCENTAGE' ? (
              <div className="p-3.5 rounded-lg bg-neutral-50 border border-neutral-200 space-y-2">
                <label className="block text-xs font-semibold text-neutral-700">
                  Increment Percentage (%)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.01"
                    value={incrementPercentage}
                    onChange={(e) => setIncrementPercentage(Number(e.target.value))}
                    placeholder="e.g. 15"
                    className="w-full pr-8 pl-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <span className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                    %
                  </span>
                </div>
                <div className="text-xs text-neutral-500">
                  Formula: Old CTC × (1 + {incrementPercentage || 0}%)
                </div>
              </div>
            ) : (
              <div className="p-3.5 rounded-lg bg-neutral-50 border border-neutral-200 space-y-2">
                <label className="block text-xs font-semibold text-neutral-700">
                  Target New Annual CTC (₹)
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                    ₹
                  </span>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={targetCTC === 0 ? '' : targetCTC}
                    onChange={(e) => setTargetCTC(Math.max(0, Number(e.target.value)))}
                    placeholder="e.g. 2400000"
                    className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div className="text-xs text-neutral-500">
                  Direct Target CTC applied to proportion distribution.
                </div>
              </div>
            )}

            {/* Live New CTC Calculation Summary Box */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-primary-900 to-primary-800 text-white shadow-md">
              <span className="text-xs text-primary-200 font-medium uppercase tracking-wider block">
                Calculated Revised CTC
              </span>
              <div className="text-2xl font-bold mt-1 text-white">
                {formatIndianCurrency(summary.calculatedNewCTC, 2)}
              </div>
              <div className="mt-2 text-xs text-primary-100 flex items-center justify-between border-t border-primary-700/60 pt-2">
                <span>Overall CTC Growth:</span>
                <span className="font-semibold text-emerald-300">
                  {summary.ctcPercentageIncrease >= 0 ? '+' : ''}
                  {formatPercentage(summary.ctcPercentageIncrease, 2)}
                </span>
              </div>
            </div>
          </GlassCard>

          {/* Validation & Reconciliation Summary Widget */}
          <GlassCard className="p-5 space-y-3">
            <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Reconciliation & Integrity
            </h3>

            {/* Mismatch Warning 1: Old components sum != Old CTC */}
            {summary.isOldSumMismatch ? (
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-amber-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                  Old Components Sum Mismatch
                </div>
                <div>
                  Sum of old components (<strong>{formatIndianCurrency(summary.totalOldComponents, 2)}</strong>) does not equal entered Old CTC (<strong>{formatIndianCurrency(summary.oldEnteredCTC, 2)}</strong>).
                </div>
                <div className="text-amber-700">
                  Difference: {formatIndianCurrency(Math.abs(summary.oldSumDifference), 2)} ({summary.oldSumDifference > 0 ? 'Surplus' : 'Deficit'}).
                </div>
                <div className="text-[11px] text-amber-600 italic">
                  Note: The workbook allows this difference; no automatic redistribution is applied.
                </div>
              </div>
            ) : (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Sum of old components matches entered Old CTC perfectly.</span>
              </div>
            )}

            {/* Mismatch Warning 2: New components sum != Target CTC */}
            {summary.isNewSumMismatch ? (
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-900 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-blue-950">
                  <Info className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                  Revised Components vs Target CTC Difference
                </div>
                <div>
                  Sum of revised components (<strong>{formatIndianCurrency(summary.totalNewComponents, 2)}</strong>) differs from Target CTC (<strong>{formatIndianCurrency(summary.calculatedNewCTC, 2)}</strong>) by <strong>{formatIndianCurrency(summary.newSumDifference, 2)}</strong>.
                </div>
                <div className="text-[11px] text-blue-700">
                  Expected behaviour: Static PF components (PFEMP, EPEMPR, EPSEMPR) remain locked at their fixed amounts and are not escalated proportionally.
                </div>
              </div>
            ) : (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Sum of revised components matches target CTC.</span>
              </div>
            )}
          </GlassCard>
        </div>

        {/* Right 2 Columns: Component Breakdown Table & Inputs */}
        <div className="lg:col-span-2 space-y-6">
          <GlassCard className="p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
              <div>
                <h2 className="text-base font-semibold text-neutral-900 flex items-center gap-2">
                  <FileSpreadsheet className="w-4 h-4 text-primary-600" />
                  Salary Components & Proportional Distribution
                </h2>
                <p className="text-xs text-neutral-500">
                  Edit Old Amount values directly. Non-static components adjust proportionally; static PF components remain locked.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                  <Lock className="w-3 h-3" /> Static PF = Locked
                </span>
              </div>
            </div>

            {/* Components Comparison Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-neutral-200 bg-neutral-50 text-neutral-600 font-semibold uppercase tracking-wider">
                    <th className="py-2.5 px-3">Component</th>
                    <th className="py-2.5 px-3 text-right">Old Annual Amount (₹)</th>
                    <th className="py-2.5 px-3 text-right">% of Old CTC</th>
                    <th className="py-2.5 px-3 text-center">PF Static?</th>
                    <th className="py-2.5 px-3 text-right font-bold text-neutral-900">New Annual Amount (₹)</th>
                    <th className="py-2.5 px-3 text-right">Difference (₹)</th>
                    <th className="py-2.5 px-2 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100 font-medium">
                  {summary.results.map((comp) => {
                    const isPF = comp.isStatic;
                    return (
                      <tr
                        key={comp.id}
                        className={`hover:bg-neutral-50/80 transition ${
                          isPF ? 'bg-amber-50/30' : ''
                        }`}
                      >
                        {/* Component Name */}
                        <td className="py-2.5 px-3">
                          <div className="font-semibold text-neutral-900 flex items-center gap-1.5">
                            {comp.name}
                            {isPF && (
                              <Lock className="w-3 h-3 text-amber-600 inline" title="Static PF component" />
                            )}
                          </div>
                          {comp.notes && (
                            <div className="text-[10px] text-neutral-400 font-normal">
                              {comp.notes}
                            </div>
                          )}
                        </td>

                        {/* Editable Old Amount */}
                        <td className="py-2.5 px-3 text-right">
                          <div className="relative inline-block w-32">
                            <input
                              type="number"
                              min="0"
                              step="1"
                              value={comp.oldAmount === 0 ? '' : comp.oldAmount}
                              onChange={(e) =>
                                handleComponentAmountChange(comp.id, Number(e.target.value))
                              }
                              className={`w-full text-right px-2 py-1 text-xs rounded border ${
                                isPF
                                  ? 'bg-amber-50 border-amber-300 text-amber-900 font-medium'
                                  : 'bg-white border-neutral-300 text-neutral-900'
                              } focus:outline-none focus:ring-1 focus:ring-primary-500`}
                            />
                          </div>
                          <div className="text-[10px] text-neutral-400">
                            Monthly: {formatIndianCurrency(comp.oldAmount / 12, 0)}
                          </div>
                        </td>

                        {/* % of Old CTC */}
                        <td className="py-2.5 px-3 text-right text-neutral-600">
                          {formatPercentage(comp.oldPercentageOfCTC * 100, 2)}
                        </td>

                        {/* PF Static Toggle */}
                        <td className="py-2.5 px-3 text-center">
                          <button
                            type="button"
                            onClick={() => handleToggleStatic(comp.id)}
                            className={`px-2 py-0.5 rounded text-[11px] font-semibold transition ${
                              comp.isStatic
                                ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                            }`}
                          >
                            {comp.isStatic ? 'Yes' : 'No'}
                          </button>
                        </td>

                        {/* New Annual Amount */}
                        <td className="py-2.5 px-3 text-right font-bold text-neutral-900">
                          <div>{formatIndianCurrency(comp.newAmount, 2)}</div>
                          <div className="text-[10px] text-neutral-500 font-normal">
                            Monthly: {formatIndianCurrency(comp.newAmount / 12, 2)}
                          </div>
                        </td>

                        {/* Difference */}
                        <td className="py-2.5 px-3 text-right font-semibold">
                          <span
                            className={
                              comp.difference > 0
                                ? 'text-emerald-700'
                                : comp.difference < 0
                                ? 'text-red-600'
                                : 'text-neutral-500'
                            }
                          >
                            {comp.difference > 0 ? '+' : ''}
                            {formatIndianCurrency(comp.difference, 2)}
                          </span>
                        </td>

                        {/* Delete custom component */}
                        <td className="py-2.5 px-2 text-center">
                          {comp.isCustom ? (
                            <button
                              type="button"
                              onClick={() => handleRemoveComponent(comp.id)}
                              className="text-neutral-400 hover:text-red-500 transition p-1"
                              title="Remove custom component"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          ) : (
                            <span className="text-neutral-300 text-xs">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>

                {/* Total Row */}
                <tfoot>
                  <tr className="border-t-2 border-neutral-300 bg-neutral-100/90 font-bold text-neutral-900 text-xs">
                    <td className="py-3 px-3 uppercase tracking-wider">Total Components</td>
                    <td className="py-3 px-3 text-right">
                      <div>{formatIndianCurrency(summary.totalOldComponents, 2)}</div>
                      <div className="text-[10px] text-neutral-500 font-normal">
                        Monthly: {formatIndianCurrency(summary.totalOldComponents / 12, 2)}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right">
                      {formatPercentage(
                        summary.oldEnteredCTC > 0
                          ? (summary.totalOldComponents / summary.oldEnteredCTC) * 100
                          : 0,
                        2
                      )}
                    </td>
                    <td className="py-3 px-3 text-center text-neutral-400">—</td>
                    <td className="py-3 px-3 text-right text-primary-900">
                      <div>{formatIndianCurrency(summary.totalNewComponents, 2)}</div>
                      <div className="text-[10px] text-primary-700 font-normal">
                        Monthly: {formatIndianCurrency(summary.totalNewComponents / 12, 2)}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right text-emerald-800">
                      {summary.totalComponentIncrease >= 0 ? '+' : ''}
                      {formatIndianCurrency(summary.totalComponentIncrease, 2)}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Add Custom Component Section */}
            <div className="pt-3 border-t border-neutral-200">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs font-semibold text-neutral-700 flex items-center gap-1">
                  <Plus className="w-3.5 h-3.5 text-primary-600" /> Add Additional Component:
                </span>
                <input
                  type="text"
                  placeholder="Component Name (e.g. Special Allowance)"
                  value={newCompName}
                  onChange={(e) => setNewCompName(e.target.value)}
                  className="px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <input
                  type="number"
                  min="0"
                  placeholder="Old Annual Amount"
                  value={newCompAmount}
                  onChange={(e) =>
                    setNewCompAmount(e.target.value === '' ? '' : Number(e.target.value))
                  }
                  className="w-36 px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <label className="flex items-center gap-1.5 text-xs text-neutral-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newCompIsStatic}
                    onChange={(e) => setNewCompIsStatic(e.target.checked)}
                    className="rounded text-primary-600 focus:ring-primary-500"
                  />
                  <span>PF Static</span>
                </label>
                <button
                  type="button"
                  onClick={handleAddComponent}
                  disabled={!newCompName.trim()}
                  className="px-3 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-40 text-white text-xs font-medium transition"
                >
                  Add
                </button>
              </div>
            </div>
          </GlassCard>

          {/* Detailed Revision Comparison & Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Entered Old CTC</span>
              <div className="text-lg font-bold text-neutral-900">
                {formatIndianCurrency(summary.oldEnteredCTC, 2)}
              </div>
              <div className="text-xs text-neutral-500">
                Sum of Old Components: {formatIndianCurrency(summary.totalOldComponents, 2)}
              </div>
            </GlassCard>

            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Target / Calculated CTC</span>
              <div className="text-lg font-bold text-primary-700">
                {formatIndianCurrency(summary.calculatedNewCTC, 2)}
              </div>
              <div className="text-xs text-neutral-500">
                Sum of New Components: {formatIndianCurrency(summary.totalNewComponents, 2)}
              </div>
            </GlassCard>

            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Total Component Increase</span>
              <div className="text-lg font-bold text-emerald-600">
                {summary.totalComponentIncrease >= 0 ? '+' : ''}
                {formatIndianCurrency(summary.totalComponentIncrease, 2)}
              </div>
              <div className="text-xs text-neutral-500">
                Actual Component Growth: {formatPercentage(summary.actualPercentageIncrease, 2)}
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
