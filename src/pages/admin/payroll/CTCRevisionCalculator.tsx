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
  UserCheck,
  CheckCircle2,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  Briefcase,
  GitBranch
} from 'lucide-react';
import {
  CTCComponentInput,
  ComponentCategory,
  CalculationMethod,
  RevisionMethod,
  DEFAULT_EXAMPLE_COMPONENTS,
  DEFAULT_EMPLOYEE_DEDUCTIONS,
  calculateCTCRevision,
  formatIndianCurrency,
  formatPercentage,
  classifyComponent
} from '../../../utils/ctcCalculatorEngine';

export default function CTCRevisionCalculatorPage() {
  // 1. Calculator State
  const [oldCTC, setOldCTC] = useState<number>(600000);
  const [revisionMethod, setRevisionMethod] = useState<RevisionMethod>('TARGET_CTC');
  const [incrementPercentage, setIncrementPercentage] = useState<number>(15);
  const [targetCTC, setTargetCTC] = useState<number>(800000);
  const [components, setComponents] = useState<CTCComponentInput[]>(DEFAULT_EXAMPLE_COMPONENTS);

  // Employee Deductions (distinct from Employer CTC cost)
  const [employeeDeductions, setEmployeeDeductions] = useState<CTCComponentInput[]>(DEFAULT_EMPLOYEE_DEDUCTIONS);
  const [showEmployeeDeductions, setShowEmployeeDeductions] = useState(false);

  // New Custom Component Inline Adder
  const [newCompName, setNewCompName] = useState('');
  const [newCompCategory, setNewCompCategory] = useState<ComponentCategory>('Earning');
  const [newCompMethod, setNewCompMethod] = useState<CalculationMethod>('Flat');
  const [newCompAmount, setNewCompAmount] = useState<number | ''>('');
  const [newCompPercentage, setNewCompPercentage] = useState<number | ''>('');
  const [newCompParentId, setNewCompParentId] = useState<string>('');

  // 2. Employee Prefill Integration State
  const [employees, setEmployees] = useState<any[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(false);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [loadingPrefill, setLoadingPrefill] = useState(false);
  const [prefillNotice, setPrefillNotice] = useState<string | null>(null);

  // Load employee directory for prefill
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
      const emp = employees.find((e) => (e.id || e._id || e.employeeId) === empId);
      const codeOrId = emp?.employeeId || emp?.employeeCode || empId;

      const configRes = await employeeApi.getSalaryConfig(codeOrId);
      const config = configRes?.data || configRes || {};

      let fetchedComponents: CTCComponentInput[] = [];

      // Check if backend returned activeComponents (full snapshot with all components)
      if (Array.isArray(config.activeComponents) && config.activeComponents.length > 0) {
        fetchedComponents = config.activeComponents.map((c: any) => {
          const compName = c.componentName || c.name || 'Component';
          const { category } = classifyComponent(compName);
          const method = (c.calculationMethod || 'Flat') as CalculationMethod;
          const annualAmt = Number(c.annualAmount) || (Number(c.monthlyAmount || 0) * 12);

          return {
            id: String(c.salaryComponentId || c._id || c.id),
            name: compName,
            category: (c.componentType === 'Deduction' ? 'Employee Deduction' : category) as ComponentCategory,
            calculationMethod: method,
            percentageValue: c.percentage !== null && c.percentage !== undefined ? Number(c.percentage) : undefined,
            percentageDerivedFromComponentId: c.percentageDerivedFromComponentId ? String(c.percentageDerivedFromComponentId) : undefined,
            defaultFormula: c.formulaUsed || undefined,
            oldAmount: annualAmt,
            notes: c.formulaUsed ? `Formula: ${c.formulaUsed}` : 'Prefilled from active employee salary structure'
          };
        });
      } else {
        // Fallback: build from basicSalary and customComponents if activeComponents is not present
        if (config.basicSalary) {
          const annualBasic = config.basicSalary * 12;
          fetchedComponents.push({
            id: 'basic',
            name: 'Basic',
            category: 'Earning',
            calculationMethod: 'Flat',
            oldAmount: annualBasic,
            notes: 'Prefilled from active employee salary structure (Annualized)'
          });
        }

        if (config.customComponents && typeof config.customComponents === 'object') {
          let compMasterMap: Record<string, any> = {};
          try {
            const allCompsRes = await organizationApi.getSalaryComponents();
            const allComps = allCompsRes?.data || allCompsRes || [];
            allComps.forEach((c: any) => {
              compMasterMap[c._id || c.id] = c;
            });
          } catch {
            // fallback
          }

          Object.entries(config.customComponents).forEach(([cid, monthlyAmt]) => {
            const master = compMasterMap[cid];
            const compName = master?.name || `Component ${cid.substring(0, 6)}`;
            const annualAmt = Number(monthlyAmt) * 12;
            const { category } = classifyComponent(compName);

            fetchedComponents.push({
              id: cid,
              name: compName,
              category,
              calculationMethod: master?.calculationMethod || 'Flat',
              percentageValue: master?.percentageValue,
              percentageDerivedFromComponentId: master?.percentageDerivedFromComponentId,
              defaultFormula: master?.defaultFormula,
              oldAmount: annualAmt,
              notes: 'Prefilled from employee configuration'
            });
          });
        }
      }

      if (fetchedComponents.length > 0) {
        // Calculate the initial Old CTC sum
        const totalFetchedOld = fetchedComponents.reduce((acc, c) => acc + (c.oldAmount || 0), 0);
        setComponents(fetchedComponents);
        setOldCTC(totalFetchedOld);
        setPrefillNotice(
          `Successfully prefilled ${fetchedComponents.length} salary components (direct and formula-derived) for ${emp?.firstName || ''} ${emp?.lastName || ''} (${codeOrId}). Read-only preview: no records will be saved or modified.`
        );
      } else {
        setPrefillNotice(
          `No active component records found for employee ${emp?.firstName || ''} ${emp?.lastName || ''}. You can configure components manually below.`
        );
      }
    } catch (e: any) {
      console.warn('Salary prefill notice:', e);
      setPrefillNotice('Employee salary structure not found or yet to be configured. You can enter or adjust components manually.');
    } finally {
      setLoadingPrefill(false);
    }
  };

  // Reset to default example values
  const handleReset = () => {
    setOldCTC(600000);
    setRevisionMethod('TARGET_CTC');
    setIncrementPercentage(15);
    setTargetCTC(800000);
    setComponents(DEFAULT_EXAMPLE_COMPONENTS);
    setEmployeeDeductions(DEFAULT_EMPLOYEE_DEDUCTIONS);
    setSelectedEmployeeId('');
    setPrefillNotice(null);
  };

  // Component Amount Change Handler
  const handleComponentAmountChange = (id: string, val: number) => {
    setComponents((prev) =>
      prev.map((c) => (c.id === id ? { ...c, oldAmount: Math.max(0, val) } : c))
    );
  };

  // Add custom component
  const handleAddComponent = () => {
    if (!newCompName.trim()) return;
    const isFormula = newCompMethod === 'Percentage' || newCompMethod === 'Formula';
    const amount = Number(newCompAmount) || 0;
    const percVal = Number(newCompPercentage) || 0;
    const newId = `custom_${Date.now()}`;

    setComponents((prev) => [
      ...prev,
      {
        id: newId,
        name: newCompName.trim(),
        category: newCompCategory,
        calculationMethod: newCompMethod,
        percentageValue: isFormula ? percVal : undefined,
        percentageDerivedFromComponentId: isFormula ? (newCompParentId || undefined) : undefined,
        defaultFormula: isFormula ? `${percVal}% of parent` : undefined,
        oldAmount: amount,
        isCustom: true,
        notes: isFormula ? `Formula-derived (${percVal}%)` : `Configured ${newCompCategory}`
      }
    ]);

    setNewCompName('');
    setNewCompAmount('');
    setNewCompPercentage('');
    setNewCompParentId('');
    setNewCompCategory('Earning');
    setNewCompMethod('Flat');
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
      components,
      employeeDeductions
    });
  }, [oldCTC, revisionMethod, incrementPercentage, targetCTC, components, employeeDeductions]);

  // Grouped presentation breakdown
  const earningsComponents = summary.results.filter((c) => c.category === 'Earning');
  const employerContributions = summary.results.filter((c) => c.category === 'Employer Contribution');
  const annualBenefits = summary.results.filter((c) => c.category === 'Annual Benefit');

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
                Full CTC architecture supporting direct input, formula-derived earnings, employer contributions, and annual benefits.
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
            Reset to Defaults
          </button>
        </div>
      </div>

      {/* Architecture Explanatory Notice */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-primary-50 via-blue-50 to-indigo-50 border border-primary-200 text-xs text-primary-950 flex items-start gap-3 shadow-sm">
        <Info className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div>
            <span className="font-semibold text-primary-900">Dependency-Aware Salary Component Engine: </span>
            The calculator accounts for every component that forms employer CTC. Formula-derived earnings (e.g., HRA as a % of Basic) are evaluated from their dependency relationships, while preserving strict CTC reconciliation. Employee-side deductions are tracked distinctly and do not inflate employer CTC.
          </div>
        </div>
      </div>

      {/* Prefill Employee Salary Structure Card */}
      <GlassCard className="p-5 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-100 pb-3">
          <div>
            <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-primary-600" />
              Prefill from Active Employee Structure (Read-Only)
            </h3>
            <p className="text-xs text-neutral-500">
              Select an employee to populate their active salary structure (including formula-derived components) into the calculator.
            </p>
          </div>

          <div className="w-full sm:w-72">
            <select
              value={selectedEmployeeId}
              onChange={(e) => handleEmployeeSelect(e.target.value)}
              disabled={loadingEmployees || loadingPrefill}
              className="w-full text-xs rounded-lg border border-neutral-300 bg-white px-3 py-2 text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-neutral-100"
            >
              <option value="">-- Select Employee to Prefill --</option>
              {employees.map((emp) => {
                const idVal = emp.id || emp._id || emp.employeeId;
                const code = emp.employeeId || emp.employeeCode || idVal;
                const name = `${emp.firstName || ''} ${emp.lastName || ''}`.trim() || emp.name || code;
                return (
                  <option key={idVal} value={idVal}>
                    {name} ({code})
                  </option>
                );
              })}
            </select>
          </div>
        </div>

        {loadingPrefill && (
          <div className="text-xs text-primary-600 flex items-center gap-2 py-1">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            Loading employee salary components and formula definitions...
          </div>
        )}

        {prefillNotice && (
          <div className="p-2.5 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-800 flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <span>{prefillNotice}</span>
          </div>
        )}
      </GlassCard>

      {/* Main Grid: Left Controls (1 Col) & Right Breakdown Table (2 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Revision Settings & Old CTC Input */}
        <div className="space-y-6">
          <GlassCard className="p-5 space-y-4">
            <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2 border-b border-neutral-100 pb-2">
              <TrendingUp className="w-4 h-4 text-primary-600" />
              Revision Method & CTC Targets
            </h3>

            {/* Old Annual CTC Input */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1">
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
                  placeholder="e.g. 600000"
                  className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="text-[11px] text-neutral-500 mt-1">
                Monthly Equivalent: {formatIndianCurrency(oldCTC / 12, 2)}
              </div>
              {oldCTC <= 0 && (
                <div className="text-[11px] text-amber-600 mt-1">
                  Old CTC must be greater than zero for proportional calculation.
                </div>
              )}
            </div>

            {/* Revision Method Selector */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1.5">
                Revision Calculation Method
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
                    placeholder="e.g. 800000"
                    className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div className="text-xs text-neutral-500">
                  Direct Target CTC applied across all components.
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
                <span>Total Increment:</span>
                <span className="font-semibold text-emerald-300">
                  {summary.totalIncrement >= 0 ? '+' : ''}
                  {formatIndianCurrency(summary.totalIncrement, 2)} (
                  {formatPercentage(summary.incrementPercentage, 2)})
                </span>
              </div>
            </div>
          </GlassCard>

          {/* Validation & Reconciliation Summary Widget */}
          <GlassCard className="p-5 space-y-3">
            <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              CTC Reconciliation & Integrity
            </h3>

            {/* Calculation warnings / dependency errors */}
            {summary.calculationWarnings && summary.calculationWarnings.length > 0 && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-xs text-red-800 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-red-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-600 flex-shrink-0" />
                  Dependency Warnings
                </div>
                {summary.calculationWarnings.map((w, idx) => (
                  <div key={idx} className="text-[11px] text-red-700">{w}</div>
                ))}
              </div>
            )}

            {/* Reconciliation Comparison Card */}
            <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200 text-xs space-y-2">
              <div className="flex justify-between items-center text-neutral-600">
                <span>Old Annual CTC:</span>
                <span className="font-semibold text-neutral-900">{formatIndianCurrency(summary.oldEnteredCTC, 2)}</span>
              </div>
              <div className="flex justify-between items-center text-neutral-600">
                <span>Old Total CTC Components:</span>
                <span className="font-semibold text-neutral-900">{formatIndianCurrency(summary.totalOldComponents, 2)}</span>
              </div>
              <div className="flex justify-between items-center border-t border-neutral-200 pt-1.5 text-neutral-600">
                <span>New Annual CTC:</span>
                <span className="font-semibold text-primary-800">{formatIndianCurrency(summary.calculatedNewCTC, 2)}</span>
              </div>
              <div className="flex justify-between items-center text-neutral-600">
                <span>New Total CTC Components:</span>
                <span className="font-semibold text-primary-800">{formatIndianCurrency(summary.totalNewComponents, 2)}</span>
              </div>
              <div className="flex justify-between items-center border-t border-neutral-200 pt-1.5 text-neutral-600">
                <span>CTC Difference:</span>
                <span className={`font-semibold ${Math.abs(summary.newSumDifference) > 0.01 ? 'text-amber-700' : 'text-emerald-700'}`}>
                  {formatIndianCurrency(summary.newSumDifference, 2)}
                </span>
              </div>
            </div>

            {/* Mismatch Warning 1: Old components sum != Old CTC */}
            {summary.isOldSumMismatch ? (
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-amber-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                  Old Components Sum Mismatch
                </div>
                <div>
                  Sum of old components (<strong>{formatIndianCurrency(summary.totalOldComponents, 2)}</strong>, {formatPercentage(summary.oldComponentsPercentageSum, 2)}) does not equal entered Old CTC (<strong>{formatIndianCurrency(summary.oldEnteredCTC, 2)}</strong>).
                </div>
                <div className="text-amber-700">
                  Difference: {formatIndianCurrency(Math.abs(summary.oldSumDifference), 2)} ({summary.oldSumDifference > 0 ? 'Surplus' : 'Deficit'}).
                </div>
              </div>
            ) : (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>All old component percentages sum to 100.00% and reconcile with Old CTC.</span>
              </div>
            )}

            {/* Mismatch Warning 2: New components sum != Target CTC */}
            {summary.isNewSumMismatch ? (
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-amber-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                  Revised Components vs Target CTC Difference
                </div>
                <div>
                  Sum of revised components (<strong>{formatIndianCurrency(summary.totalNewComponents, 2)}</strong>) differs from Target CTC (<strong>{formatIndianCurrency(summary.calculatedNewCTC, 2)}</strong>) by <strong>{formatIndianCurrency(summary.newSumDifference, 2)}</strong> due to old input mismatch.
                </div>
              </div>
            ) : (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>New component amounts reconcile 100.00% with the target New CTC.</span>
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
                  <Layers className="w-4 h-4 text-primary-600" />
                  Salary Breakdown & Proportional Comparison
                </h2>
                <p className="text-xs text-neutral-500">
                  Comparison of all CTC components, including direct input and formula-derived earnings.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowEmployeeDeductions(!showEmployeeDeductions)}
                  className="text-xs text-primary-700 bg-primary-50 hover:bg-primary-100 px-2.5 py-1 rounded-md border border-primary-200 transition"
                >
                  {showEmployeeDeductions ? 'Hide Employee Deductions' : 'Show Employee Deductions'}
                </button>
              </div>
            </div>

            {/* Components Comparison Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-neutral-200 bg-neutral-50 text-neutral-600 font-semibold uppercase tracking-wider">
                    <th className="py-2.5 px-3">Component</th>
                    <th className="py-2.5 px-2">Component Type</th>
                    <th className="py-2.5 px-2">Calculation Method</th>
                    <th className="py-2.5 px-3 text-right">Old Annual Amount</th>
                    <th className="py-2.5 px-3 text-right">Old CTC %</th>
                    <th className="py-2.5 px-3 text-right font-bold text-neutral-900">New Annual Amount</th>
                    <th className="py-2.5 px-3 text-right">New CTC %</th>
                    <th className="py-2.5 px-2 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100 font-medium">
                  {summary.results.map((comp) => {
                    const isAnnual = comp.isAnnualPayout;
                    const isFormula = comp.isFormulaDerived;
                    return (
                      <tr
                        key={comp.id}
                        className={`hover:bg-neutral-50/80 transition ${
                          isAnnual ? 'bg-blue-50/30' : comp.category === 'Employer Contribution' ? 'bg-emerald-50/30' : isFormula ? 'bg-purple-50/20' : ''
                        }`}
                      >
                        {/* Component Name */}
                        <td className="py-2.5 px-3">
                          <div className="font-semibold text-neutral-900 flex items-center gap-1.5">
                            {comp.name}
                            {isAnnual && (
                              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 text-blue-800" title="Paid/processed annually">
                                <Calendar className="w-2.5 h-2.5" /> Annual Benefit
                              </span>
                            )}
                          </div>
                          {comp.notes && (
                            <div className="text-[10px] text-neutral-400 font-normal">
                              {comp.notes}
                            </div>
                          )}
                          {comp.evaluationError && (
                            <div className="text-[10px] text-red-500 font-normal">
                              {comp.evaluationError}
                            </div>
                          )}
                        </td>

                        {/* Component Type */}
                        <td className="py-2.5 px-2">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${
                              comp.category === 'Earning'
                                ? 'bg-neutral-100 text-neutral-700'
                                : comp.category === 'Employer Contribution'
                                ? 'bg-emerald-100 text-emerald-800'
                                : comp.category === 'Annual Benefit'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-purple-100 text-purple-800'
                            }`}
                          >
                            {comp.category}
                          </span>
                        </td>

                        {/* Calculation Method */}
                        <td className="py-2.5 px-2">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${
                              comp.displayCalculationMethod === 'Direct Input'
                                ? 'bg-gray-100 text-gray-700'
                                : comp.displayCalculationMethod === 'Formula Derived'
                                ? 'bg-purple-100 text-purple-800 font-semibold'
                                : comp.displayCalculationMethod === 'Employer Contribution'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {comp.displayCalculationMethod}
                          </span>
                          {isFormula && comp.formulaDescription && (
                            <div className="text-[10px] text-purple-700 mt-0.5 flex items-center gap-1 font-normal">
                              <GitBranch className="w-2.5 h-2.5 flex-shrink-0" />
                              <span>{comp.formulaDescription}</span>
                            </div>
                          )}
                        </td>

                        {/* Editable Old Amount (or calculated formula amount) */}
                        <td className="py-2.5 px-3 text-right">
                          {isFormula ? (
                            <div>
                              <span className="font-semibold text-neutral-900">{formatIndianCurrency(comp.oldAmount, 2)}</span>
                              <div className="text-[10px] text-purple-600">Calculated from formula</div>
                            </div>
                          ) : (
                            <div className="relative inline-block w-28">
                              <input
                                type="number"
                                min="0"
                                step="1"
                                value={comp.oldAmount === 0 ? '' : comp.oldAmount}
                                onChange={(e) =>
                                  handleComponentAmountChange(comp.id, Number(e.target.value))
                                }
                                className="w-full text-right px-2 py-1 text-xs rounded border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-1 focus:ring-primary-500"
                              />
                            </div>
                          )}
                          <div className="text-[10px] text-neutral-400">
                            {isAnnual ? 'Annual amount' : `Monthly: ${formatIndianCurrency(comp.oldAmount / 12, 0)}`}
                          </div>
                        </td>

                        {/* Old % of CTC */}
                        <td className="py-2.5 px-3 text-right text-neutral-700 font-semibold">
                          {formatPercentage(comp.oldPercentageOfCTC, 2)}
                        </td>

                        {/* New Annual Amount */}
                        <td className="py-2.5 px-3 text-right font-bold text-neutral-900">
                          <div>{formatIndianCurrency(comp.newAmount, 2)}</div>
                          <div className="text-[10px] text-emerald-700 font-normal">
                            {comp.difference >= 0 ? '+' : ''}
                            {formatIndianCurrency(comp.difference, 2)}
                          </div>
                        </td>

                        {/* New % of CTC */}
                        <td className="py-2.5 px-3 text-right text-neutral-600">
                          {formatPercentage(comp.newPercentageOfCTC, 2)}
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
                    <td className="py-3 px-3 uppercase tracking-wider" colSpan={3}>
                      Total Complete CTC Components
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div>{formatIndianCurrency(summary.totalOldComponents, 2)}</div>
                      <div className="text-[10px] text-neutral-500 font-normal">
                        Monthly: {formatIndianCurrency(summary.totalOldComponents / 12, 0)}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right text-primary-900">
                      {formatPercentage(summary.oldComponentsPercentageSum, 2)}
                    </td>
                    <td className="py-3 px-3 text-right text-primary-900 font-extrabold text-sm">
                      <div>{formatIndianCurrency(summary.totalNewComponents, 2)}</div>
                      <div className="text-[10px] text-emerald-700 font-normal">
                        {summary.totalIncrement >= 0 ? '+' : ''}
                        {formatIndianCurrency(summary.totalIncrement, 2)}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-right text-neutral-700">
                      {formatPercentage(
                        summary.calculatedNewCTC > 0
                          ? (summary.totalNewComponents / summary.calculatedNewCTC) * 100
                          : 0,
                        2
                      )}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {/* Separate Employee Deductions Section (Distinct from Employer CTC Cost) */}
            {showEmployeeDeductions && (
              <div className="mt-4 p-4 rounded-xl bg-neutral-50 border border-neutral-200 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-neutral-600" />
                    <span className="text-xs font-semibold text-neutral-900 uppercase tracking-wider">
                      Employee-Side Deductions (Reference Only - Deducted from Gross, Not Employer CTC Cost)
                    </span>
                  </div>
                  <span className="text-[11px] text-neutral-500">
                    Employee PF and statutory deductions are deducted from the employee's gross earnings. They are NOT employer CTC costs.
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-neutral-200 bg-neutral-100 text-neutral-600 font-semibold uppercase">
                        <th className="py-2 px-3">Deduction Component</th>
                        <th className="py-2 px-3 text-right">Old Deduction (₹)</th>
                        <th className="py-2 px-3 text-right">Revised Deduction (₹)</th>
                        <th className="py-2 px-3 text-right">Monthly Deduction (₹)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-200 font-medium">
                      {summary.employeeDeductionResults?.map((ded) => (
                        <tr key={ded.id} className="hover:bg-neutral-100/50">
                          <td className="py-2.5 px-3">
                            <span className="font-semibold text-neutral-800">{ded.name}</span>
                            <span className="ml-2 text-[10px] text-neutral-400">({ded.category})</span>
                          </td>
                          <td className="py-2.5 px-3 text-right text-neutral-700">
                            {formatIndianCurrency(ded.oldAmount, 2)}
                          </td>
                          <td className="py-2.5 px-3 text-right font-semibold text-neutral-900">
                            {formatIndianCurrency(ded.newAmount, 2)}
                          </td>
                          <td className="py-2.5 px-3 text-right text-neutral-700">
                            {formatIndianCurrency(ded.monthlyEquivalent, 2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

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
                <select
                  value={newCompCategory}
                  onChange={(e) => setNewCompCategory(e.target.value as ComponentCategory)}
                  className="px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="Earning">Earning</option>
                  <option value="Employer Contribution">Employer Contribution</option>
                  <option value="Annual Benefit">Annual Benefit</option>
                  <option value="Other CTC Component">Other CTC Component</option>
                </select>
                <select
                  value={newCompMethod}
                  onChange={(e) => setNewCompMethod(e.target.value as CalculationMethod)}
                  className="px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="Flat">Direct Input (Flat)</option>
                  <option value="Percentage">Formula (% of Parent)</option>
                </select>

                {newCompMethod === 'Percentage' ? (
                  <>
                    <input
                      type="number"
                      min="0"
                      placeholder="Percentage (%)"
                      value={newCompPercentage}
                      onChange={(e) => setNewCompPercentage(e.target.value === '' ? '' : Number(e.target.value))}
                      className="w-24 px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    />
                    <select
                      value={newCompParentId}
                      onChange={(e) => setNewCompParentId(e.target.value)}
                      className="px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      <option value="">-- Select Parent Component --</option>
                      {components.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </>
                ) : (
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
                )}

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

          {/* Categorized Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Monthly Recurring Earnings</span>
              <div className="text-lg font-bold text-neutral-900">
                {formatIndianCurrency(
                  earningsComponents.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-xs text-neutral-500">
                Monthly Payout: {formatIndianCurrency(
                  earningsComponents.reduce((acc, c) => acc + c.monthlyEquivalent, 0),
                  2
                )}
              </div>
            </GlassCard>

            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Employer Contributions</span>
              <div className="text-lg font-bold text-emerald-700">
                {formatIndianCurrency(
                  employerContributions.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-xs text-neutral-500">
                Employer PF & Pension: {formatPercentage(
                  employerContributions.reduce((acc, c) => acc + c.newPercentageOfCTC, 0),
                  2
                )} of CTC
              </div>
            </GlassCard>

            <GlassCard className="p-4 space-y-1">
              <span className="text-xs text-neutral-500 font-medium">Annual Benefits (LTA & Gratuity)</span>
              <div className="text-lg font-bold text-blue-700">
                {formatIndianCurrency(
                  annualBenefits.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-xs text-blue-600">
                Annual Payout / Accrual (Processed annually)
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
