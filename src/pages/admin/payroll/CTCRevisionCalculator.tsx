import React, { useState, useEffect, useMemo } from 'react';
import { GlassCard } from '../../../components/ui';
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
  GitBranch,
  Gift,
  Receipt,
  Sparkles
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
  // --- Section A: Employee Selection & Retrieval State ---
  const [employees, setEmployees] = useState<any[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(false);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
  const [selectedEmployeeData, setSelectedEmployeeData] = useState<any>(null);
  const [loadingPrefill, setLoadingPrefill] = useState(false);
  const [prefillNotice, setPrefillNotice] = useState<string | null>(null);

  // Existing Stored Salary State
  const [existingAnnualCTC, setExistingAnnualCTC] = useState<number>(560000);
  const [components, setComponents] = useState<CTCComponentInput[]>(DEFAULT_EXAMPLE_COMPONENTS);
  const [employeeDeductions, setEmployeeDeductions] = useState<CTCComponentInput[]>(DEFAULT_EMPLOYEE_DEDUCTIONS);
  const [showEmployeeDeductions, setShowEmployeeDeductions] = useState(false);

  // --- Section C: Additional CTC Components State ---
  const [additionalBonus, setAdditionalBonus] = useState<number>(30000);
  const [additionalCharges, setAdditionalCharges] = useState<number>(10000);
  const [additionalComponents, setAdditionalComponents] = useState<CTCComponentInput[]>([]);

  // Inline Custom Component Input
  const [newCompName, setNewCompName] = useState('');
  const [newCompCategory, setNewCompCategory] = useState<ComponentCategory>('Earning');
  const [newCompMethod, setNewCompMethod] = useState<CalculationMethod>('Flat');
  const [newCompAmount, setNewCompAmount] = useState<number | ''>('');
  const [newCompPercentage, setNewCompPercentage] = useState<number | ''>('');
  const [newCompParentId, setNewCompParentId] = useState<string>('');

  // --- Section D: Revised CTC Target State ---
  const [revisionMethod, setRevisionMethod] = useState<RevisionMethod>('TARGET_CTC');
  const [incrementPercentage, setIncrementPercentage] = useState<number>(15);
  const [targetCTC, setTargetCTC] = useState<number>(750000);

  // Load employee directory on mount
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

  // Section A Handler: Select Employee & Retrieve Complete Salary Structure
  const handleEmployeeSelect = async (empId: string) => {
    setSelectedEmployeeId(empId);
    setPrefillNotice(null);
    setSelectedEmployeeData(null);
    if (!empId) return;

    setLoadingPrefill(true);
    try {
      const emp = employees.find((e) => (e.id || e._id || e.employeeId) === empId);
      const codeOrId = emp?.employeeId || emp?.employeeCode || empId;
      setSelectedEmployeeData(emp);

      const configRes = await employeeApi.getSalaryConfig(codeOrId);
      const config = configRes?.data || configRes || {};

      const fetchedComponents: CTCComponentInput[] = [];
      const fetchedDeductions: CTCComponentInput[] = [];

      // 1. Check if backend returned activeComponents (from employee_salary_components snapshot)
      if (Array.isArray(config.activeComponents) && config.activeComponents.length > 0) {
        config.activeComponents.forEach((c: any) => {
          const compName = c.componentName || c.name || 'Component';
          const method = (c.calculationMethod || 'Flat') as CalculationMethod;
          const annualAmt = Number(c.annualAmount) || (Number(c.monthlyAmount || 0) * 12);
          const { category } = classifyComponent(compName);

          if (c.componentType === 'Deduction' || category === 'Employee Deduction') {
            fetchedDeductions.push({
              id: String(c.salaryComponentId || c._id || c.id),
              name: compName,
              category: 'Employee Deduction',
              calculationMethod: method,
              oldAmount: annualAmt,
              notes: 'Employee-side deduction (deducted from gross)'
            });
          } else {
            fetchedComponents.push({
              id: String(c.salaryComponentId || c._id || c.id),
              name: compName,
              category,
              calculationMethod: method,
              percentageValue: c.percentage !== null && c.percentage !== undefined ? Number(c.percentage) : undefined,
              percentageDerivedFromComponentId: c.percentageDerivedFromComponentId ? String(c.percentageDerivedFromComponentId) : undefined,
              defaultFormula: c.formulaUsed || undefined,
              oldAmount: annualAmt,
              notes: c.formulaUsed ? `Formula: ${c.formulaUsed}` : 'Earning component from active structure'
            });
          }
        });
      } else {
        // Fallback: build from basicSalary and customComponents
        if (config.basicSalary) {
          const annualBasic = config.basicSalary * 12;
          fetchedComponents.push({
            id: 'basic',
            name: 'Basic',
            category: 'Earning',
            calculationMethod: 'Flat',
            oldAmount: annualBasic,
            notes: 'Basic salary component (Annualized)'
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

            if (category === 'Employee Deduction') {
              fetchedDeductions.push({
                id: cid,
                name: compName,
                category: 'Employee Deduction',
                calculationMethod: master?.calculationMethod || 'Flat',
                oldAmount: annualAmt
              });
            } else {
              fetchedComponents.push({
                id: cid,
                name: compName,
                category,
                calculationMethod: master?.calculationMethod || 'Flat',
                percentageValue: master?.percentageValue,
                percentageDerivedFromComponentId: master?.percentageDerivedFromComponentId,
                defaultFormula: master?.defaultFormula,
                oldAmount: annualAmt
              });
            }
          });
        }
      }

      // 2. Incorporate Employer Contributions (Employer PF, Employer Pension/EPS, Employer ESI, Admin Charges)
      if (Array.isArray(config.employerContributions) && config.employerContributions.length > 0) {
        config.employerContributions.forEach((ec: any, idx: number) => {
          const monthly = Number(ec.amount) || 0;
          if (monthly > 0) {
            fetchedComponents.push({
              id: `er_contrib_${idx}`,
              name: ec.name,
              category: 'Employer Contribution',
              calculationMethod: 'Flat',
              oldAmount: monthly * 12,
              notes: 'Statutory employer contribution (Part of CTC)'
            });
          }
        });
      }

      // Deductions fallback if none retrieved
      if (fetchedDeductions.length > 0) {
        setEmployeeDeductions(fetchedDeductions);
      }

      // Determine Stored / Configured Annual CTC
      let storedCTC = 0;
      if (config.summary && config.summary.annualCtc) {
        storedCTC = Number(config.summary.annualCtc);
      } else {
        storedCTC = fetchedComponents.reduce((sum, c) => sum + (c.oldAmount || 0), 0);
      }

      if (fetchedComponents.length > 0) {
        setComponents(fetchedComponents);
        setExistingAnnualCTC(storedCTC);
        setPrefillNotice(
          `Successfully retrieved salary structure for ${emp?.firstName || ''} ${emp?.lastName || ''} (${codeOrId}): ${fetchedComponents.length} CTC components loaded (including formula-derived earnings and employer statutory contributions).`
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
    setSelectedEmployeeId('');
    setSelectedEmployeeData(null);
    setPrefillNotice(null);
    setExistingAnnualCTC(560000);
    setAdditionalBonus(30000);
    setAdditionalCharges(10000);
    setAdditionalComponents([]);
    setRevisionMethod('TARGET_CTC');
    setIncrementPercentage(15);
    setTargetCTC(750000);
    setComponents(DEFAULT_EXAMPLE_COMPONENTS);
    setEmployeeDeductions(DEFAULT_EMPLOYEE_DEDUCTIONS);
  };

  // Component Amount Change Handler (Section B)
  const handleComponentAmountChange = (id: string, val: number) => {
    setComponents((prev) =>
      prev.map((c) => (c.id === id ? { ...c, oldAmount: Math.max(0, val) } : c))
    );
  };

  // Add custom component to Section B / Section C
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

  // --- Core Calculation Call: Recalculates Complete CTC Distribution & Revised Breakdown ---
  const summary = useMemo(() => {
    return calculateCTCRevision({
      existingAnnualCTC,
      additionalBonus,
      additionalCharges,
      additionalComponents,
      revisionMethod,
      incrementPercentage,
      targetCTC,
      components,
      employeeDeductions
    });
  }, [
    existingAnnualCTC,
    additionalBonus,
    additionalCharges,
    additionalComponents,
    revisionMethod,
    incrementPercentage,
    targetCTC,
    components,
    employeeDeductions
  ]);

  // Grouped presentation breakdown
  const earningsComponents = summary.results.filter((c) => c.category === 'Earning');
  const employerContributions = summary.results.filter((c) => c.category === 'Employer Contribution');
  const annualBenefits = summary.results.filter((c) => c.category === 'Annual Benefit');
  const additionalItems = summary.results.filter((c) => c.isAdditional);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Title & Reset Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-primary-100 text-primary-700">
              <Calculator className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">CTC Revision Calculator</h1>
              <p className="text-sm text-neutral-500">
                Workflow: Select Employee → Fetch Structure → Add Bonus/Charges → Recalculate 100% CTC Distribution → Enter New CTC → Generate Revised Breakdown.
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
            Reset
          </button>
        </div>
      </div>

      {/* Explanatory Banner: 100% Incorporation Rule */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-primary-50 via-blue-50 to-indigo-50 border border-primary-200 text-xs text-primary-950 flex items-start gap-3 shadow-sm">
        <Sparkles className="w-5 h-5 text-primary-600 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-primary-900">
            Mandatory Complete CTC Workflow:
          </div>
          <div>
            Additional Bonus and Additional Charges are integrated directly into the <strong>Updated Baseline CTC</strong> before calculating component percentages. Every component percentage is derived against the updated total so that the entire structure sums to <strong>100.00%</strong>. When a new CTC is entered, the revised salary breakdown scales proportionally across every component.
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SECTION A: Employee Selection and Salary Retrieval                        */}
      {/* ========================================================================= */}
      <GlassCard className="p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-100 pb-3">
          <div>
            <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-bold">
                A
              </span>
              Employee Selection & Salary Retrieval
            </h3>
            <p className="text-xs text-neutral-500">
              Select an employee to fetch their existing salary structure (Earnings, Formula-derived components, Employer PF, Employer ESI, LTA, Gratuity).
            </p>
          </div>

          <div className="w-full sm:w-80">
            <select
              value={selectedEmployeeId}
              onChange={(e) => handleEmployeeSelect(e.target.value)}
              disabled={loadingEmployees || loadingPrefill}
              className="w-full text-xs rounded-lg border border-neutral-300 bg-white px-3 py-2 text-neutral-800 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-neutral-100"
            >
              <option value="">-- Select Existing Employee --</option>
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
          <div className="text-xs text-primary-600 flex items-center gap-2 py-2">
            <RefreshCw className="w-4 h-4 animate-spin" />
            Fetching employee salary configuration, active components, and statutory employer contributions...
          </div>
        )}

        {prefillNotice && (
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <span>{prefillNotice}</span>
          </div>
        )}

        {/* Employee Summary Info Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1 text-xs">
          <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
            <span className="text-neutral-500 block">Selected Employee</span>
            <span className="font-semibold text-neutral-900">
              {selectedEmployeeData
                ? `${selectedEmployeeData.firstName || ''} ${selectedEmployeeData.lastName || ''} (${selectedEmployeeData.employeeId || selectedEmployeeId})`
                : 'Sample / Custom Mode'}
            </span>
          </div>
          <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
            <span className="text-neutral-500 block">Existing Annual CTC</span>
            <span className="font-bold text-neutral-900">
              {formatIndianCurrency(summary.existingAnnualCTC, 2)}
            </span>
          </div>
          <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
            <span className="text-neutral-500 block">Existing Components Sum</span>
            <span className="font-semibold text-neutral-900">
              {formatIndianCurrency(summary.totalExistingComponents, 2)}
            </span>
          </div>
          <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200">
            <span className="text-neutral-500 block">Reconciliation Status</span>
            <span
              className={`font-semibold inline-flex items-center gap-1 ${
                summary.isExistingMismatch ? 'text-amber-600' : 'text-emerald-600'
              }`}
            >
              {summary.isExistingMismatch ? (
                <>
                  <AlertTriangle className="w-3.5 h-3.5" /> Diff: {formatIndianCurrency(summary.existingMismatchDifference, 2)}
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" /> Components Reconciled
                </>
              )}
            </span>
          </div>
        </div>
      </GlassCard>

      {/* ========================================================================= */}
      {/* SECTION B & C: Existing Breakdown & Additional Bonus / Charges           */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: SECTION C (Additional Components) & SECTION D (Revised Target CTC) */}
        <div className="space-y-6">
          {/* SECTION C: Additional Bonus and Additional Charges */}
          <GlassCard className="p-5 space-y-4">
            <div className="border-b border-neutral-100 pb-2">
              <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-bold">
                  C
                </span>
                Additional CTC Components
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Incorporate Bonus & Charges into the complete Baseline CTC before deriving percentages.
              </p>
            </div>

            {/* Additional Bonus Input */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1 flex items-center gap-1.5">
                <Gift className="w-3.5 h-3.5 text-purple-600" /> Additional Annual Bonus (₹)
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                  ₹
                </span>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={additionalBonus === 0 ? '' : additionalBonus}
                  onChange={(e) => setAdditionalBonus(Math.max(0, Number(e.target.value)))}
                  placeholder="e.g. 30000"
                  className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="text-[11px] text-neutral-500 mt-1">
                Included in 100% baseline CTC allocation (Paid annually).
              </div>
            </div>

            {/* Additional Charges Input */}
            <div>
              <label className="block text-xs font-semibold text-neutral-700 mb-1 flex items-center gap-1.5">
                <Receipt className="w-3.5 h-3.5 text-amber-600" /> Additional Employer Charges (₹)
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                  ₹
                </span>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={additionalCharges === 0 ? '' : additionalCharges}
                  onChange={(e) => setAdditionalCharges(Math.max(0, Number(e.target.value)))}
                  placeholder="e.g. 10000"
                  className="w-full pl-8 pr-3 py-2 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="text-[11px] text-neutral-500 mt-1">
                Employer-side operational or administrative charges.
              </div>
            </div>

            {/* Complete Baseline CTC Summary Box */}
            <div className="p-3.5 rounded-xl bg-neutral-900 text-white space-y-1.5 shadow-sm">
              <span className="text-[11px] text-neutral-400 uppercase tracking-wider block font-medium">
                Updated Baseline CTC (100% Distribution Base)
              </span>
              <div className="text-xl font-bold text-white">
                {formatIndianCurrency(summary.updatedBaselineCTC, 2)}
              </div>
              <div className="text-[11px] text-neutral-300 flex justify-between border-t border-neutral-800 pt-1.5">
                <span>Existing Components:</span>
                <span>{formatIndianCurrency(summary.totalExistingComponents, 2)}</span>
              </div>
              <div className="text-[11px] text-neutral-300 flex justify-between">
                <span>Bonus & Charges:</span>
                <span className="text-emerald-300">+{formatIndianCurrency(summary.totalAdditionalAmount, 2)}</span>
              </div>
              <div className="text-[11px] text-emerald-400 font-semibold flex justify-between border-t border-neutral-800 pt-1">
                <span>Baseline Percentage Sum:</span>
                <span>{formatPercentage(summary.baselineComponentsPercentageSum, 2)}</span>
              </div>
            </div>
          </GlassCard>

          {/* SECTION D: Revised CTC Target Input */}
          <GlassCard className="p-5 space-y-4">
            <div className="border-b border-neutral-100 pb-2">
              <h3 className="text-sm font-semibold text-neutral-900 flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-bold">
                  D
                </span>
                Revised CTC Revision Target
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Apply revision across all components using recalculated component percentages.
              </p>
            </div>

            {/* Method Selector */}
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setRevisionMethod('PERCENTAGE')}
                className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs font-medium transition ${
                  revisionMethod === 'PERCENTAGE'
                    ? 'border-primary-500 bg-primary-50 text-primary-800 ring-1 ring-primary-400'
                    : 'border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50'
                }`}
              >
                <Percent className="w-4 h-4 mb-1" />
                <span>Percentage Increment</span>
              </button>

              <button
                type="button"
                onClick={() => setRevisionMethod('TARGET_CTC')}
                className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs font-medium transition ${
                  revisionMethod === 'TARGET_CTC'
                    ? 'border-primary-500 bg-primary-50 text-primary-800 ring-1 ring-primary-400'
                    : 'border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50'
                }`}
              >
                <DollarSign className="w-4 h-4 mb-1" />
                <span>Direct Target CTC</span>
              </button>
            </div>

            {/* Mode Specific Input */}
            {revisionMethod === 'PERCENTAGE' ? (
              <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200 space-y-1.5">
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
                    className="w-full pr-8 pl-3 py-1.5 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <span className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-neutral-500 text-sm">
                    %
                  </span>
                </div>
                <div className="text-[11px] text-neutral-500">
                  Formula: {formatIndianCurrency(summary.updatedBaselineCTC, 0)} × (1 + {incrementPercentage || 0}%)
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-neutral-50 border border-neutral-200 space-y-1.5">
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
                    placeholder="e.g. 750000"
                    className="w-full pl-8 pr-3 py-1.5 text-sm font-semibold rounded-lg border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
            )}

            {/* Revised CTC Box */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-primary-900 to-primary-800 text-white shadow-md">
              <span className="text-[11px] text-primary-200 font-medium uppercase tracking-wider block">
                Calculated Revised CTC
              </span>
              <div className="text-2xl font-bold mt-1 text-white">
                {formatIndianCurrency(summary.calculatedNewCTC, 2)}
              </div>
              <div className="mt-2 text-xs text-primary-100 flex items-center justify-between border-t border-primary-700/60 pt-2">
                <span>Total Growth:</span>
                <span className="font-semibold text-emerald-300">
                  {summary.totalIncrement >= 0 ? '+' : ''}
                  {formatIndianCurrency(summary.totalIncrement, 2)} (
                  {formatPercentage(summary.incrementPercentage, 2)})
                </span>
              </div>
            </div>

            {/* Reconciliation Warning */}
            {summary.isNewSumMismatch ? (
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
                <div className="font-semibold flex items-center gap-1.5 text-amber-900">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                  Revised Allocation Mismatch
                </div>
                <div>
                  Sum of components differs from Target CTC by {formatIndianCurrency(summary.newSumDifference, 2)}.
                </div>
              </div>
            ) : (
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Revised components reconcile 100.00% with target CTC.</span>
              </div>
            )}
          </GlassCard>
        </div>

        {/* Right 2 Columns: SECTION B & E (Breakdown Tables) */}
        <div className="lg:col-span-2 space-y-6">
          {/* ========================================================================= */}
          {/* SECTION B & E: Complete Salary Breakdown Table                            */}
          {/* ========================================================================= */}
          <GlassCard className="p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-neutral-200 pb-3">
              <div>
                <h2 className="text-base font-semibold text-neutral-900 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-bold">
                    E
                  </span>
                  Complete Salary Breakdown & CTC Reconciliation
                </h2>
                <p className="text-xs text-neutral-500">
                  Includes All Earnings, Formula-Derived Components, Employer Contributions, Annual Benefits & Additional Bonus/Charges.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setShowEmployeeDeductions(!showEmployeeDeductions)}
                className="text-xs text-primary-700 bg-primary-50 hover:bg-primary-100 px-2.5 py-1 rounded-md border border-primary-200 transition"
              >
                {showEmployeeDeductions ? 'Hide Employee Deductions' : 'Show Employee Deductions'}
              </button>
            </div>

            {/* Comparison Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-neutral-200 bg-neutral-50 text-neutral-600 font-semibold uppercase tracking-wider">
                    <th className="py-2.5 px-3">Component</th>
                    <th className="py-2.5 px-2">Category</th>
                    <th className="py-2.5 px-2">Calculation Method</th>
                    <th className="py-2.5 px-3 text-right">Old Annual Amount</th>
                    <th className="py-2.5 px-3 text-right font-semibold text-neutral-800">Baseline Amount</th>
                    <th className="py-2.5 px-3 text-right">Baseline CTC %</th>
                    <th className="py-2.5 px-3 text-right font-bold text-neutral-900">New Annual Amount</th>
                    <th className="py-2.5 px-2 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100 font-medium">
                  {summary.results.map((comp) => {
                    const isAnnual = comp.isAnnualPayout;
                    const isFormula = comp.isFormulaDerived;
                    const isAdditional = comp.isAdditional;

                    return (
                      <tr
                        key={comp.id}
                        className={`hover:bg-neutral-50/80 transition ${
                          isAdditional
                            ? 'bg-amber-50/40'
                            : isAnnual
                            ? 'bg-blue-50/30'
                            : comp.category === 'Employer Contribution'
                            ? 'bg-emerald-50/30'
                            : isFormula
                            ? 'bg-purple-50/20'
                            : ''
                        }`}
                      >
                        {/* Component Name */}
                        <td className="py-2.5 px-3">
                          <div className="font-semibold text-neutral-900 flex items-center gap-1.5">
                            {comp.name}
                            {isAnnual && (
                              <span
                                className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-100 text-blue-800"
                                title="Paid/processed annually, not an ordinary monthly cash payout"
                              >
                                <Calendar className="w-2.5 h-2.5" /> Annual Benefit
                              </span>
                            )}
                            {isAdditional && (
                              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-100 text-amber-800">
                                Addition
                              </span>
                            )}
                          </div>
                          {comp.notes && (
                            <div className="text-[10px] text-neutral-400 font-normal">{comp.notes}</div>
                          )}
                          {comp.evaluationError && (
                            <div className="text-[10px] text-red-500 font-normal">{comp.evaluationError}</div>
                          )}
                        </td>

                        {/* Category */}
                        <td className="py-2.5 px-2">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${
                              comp.category === 'Earning'
                                ? 'bg-neutral-100 text-neutral-700'
                                : comp.category === 'Employer Contribution'
                                ? 'bg-emerald-100 text-emerald-800'
                                : comp.category === 'Annual Benefit'
                                ? 'bg-blue-100 text-blue-800'
                                : comp.category === 'Additional Component'
                                ? 'bg-amber-100 text-amber-800'
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
                                : comp.displayCalculationMethod === 'Additional Bonus'
                                ? 'bg-purple-100 text-purple-800'
                                : comp.displayCalculationMethod === 'Additional Charges'
                                ? 'bg-amber-100 text-amber-800'
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

                        {/* Old Annual Amount (Editable for direct components, formula for derived, '-' for additions) */}
                        <td className="py-2.5 px-3 text-right">
                          {isAdditional ? (
                            <span className="text-neutral-400">—</span>
                          ) : isFormula ? (
                            <div>
                              <span className="font-semibold text-neutral-800">
                                {formatIndianCurrency(comp.oldAmount, 2)}
                              </span>
                              <div className="text-[10px] text-purple-600">Formula Derived</div>
                            </div>
                          ) : (
                            <div className="relative inline-block w-24">
                              <input
                                type="number"
                                min="0"
                                step="1"
                                value={comp.oldAmount === 0 ? '' : comp.oldAmount}
                                onChange={(e) => handleComponentAmountChange(comp.id, Number(e.target.value))}
                                className="w-full text-right px-2 py-1 text-xs rounded border border-neutral-300 bg-white text-neutral-900 focus:outline-none focus:ring-1 focus:ring-primary-500"
                              />
                            </div>
                          )}
                        </td>

                        {/* Updated Baseline Amount */}
                        <td className="py-2.5 px-3 text-right font-semibold text-neutral-900">
                          <div>{formatIndianCurrency(comp.baselineAmount, 2)}</div>
                          <div className="text-[10px] text-neutral-400 font-normal">
                            {isAnnual ? 'Annual Payout' : `Monthly: ${formatIndianCurrency(comp.baselineAmount / 12, 0)}`}
                          </div>
                        </td>

                        {/* Baseline CTC % */}
                        <td className="py-2.5 px-3 text-right text-primary-900 font-semibold">
                          {formatPercentage(comp.baselinePercentageOfCTC, 2)}
                        </td>

                        {/* New Annual Amount */}
                        <td className="py-2.5 px-3 text-right font-bold text-neutral-900">
                          <div>{formatIndianCurrency(comp.newAmount, 2)}</div>
                          <div className="text-[10px] text-emerald-700 font-normal">
                            {comp.difference >= 0 ? '+' : ''}
                            {formatIndianCurrency(comp.difference, 2)}
                          </div>
                        </td>

                        {/* Action: Delete custom component */}
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

                {/* Total Reconciliation Row */}
                <tfoot>
                  <tr className="border-t-2 border-neutral-300 bg-neutral-100/90 font-bold text-neutral-900 text-xs">
                    <td className="py-3 px-3 uppercase tracking-wider" colSpan={3}>
                      Total Complete Baseline CTC & Allocation
                    </td>
                    <td className="py-3 px-3 text-right text-neutral-600">
                      {formatIndianCurrency(summary.totalExistingComponents, 2)}
                    </td>
                    <td className="py-3 px-3 text-right text-neutral-900">
                      {formatIndianCurrency(summary.updatedBaselineCTC, 2)}
                    </td>
                    <td className="py-3 px-3 text-right text-primary-900">
                      {formatPercentage(summary.baselineComponentsPercentageSum, 2)}
                    </td>
                    <td className="py-3 px-3 text-right text-primary-900 font-extrabold text-sm">
                      <div>{formatIndianCurrency(summary.totalNewComponents, 2)}</div>
                      <div className="text-[10px] text-emerald-700 font-normal">
                        {summary.totalIncrement >= 0 ? '+' : ''}
                        {formatIndianCurrency(summary.totalIncrement, 2)}
                      </div>
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
                    Employee PF and ESI are deducted from employee gross salary. They are NOT employer CTC costs.
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
                  <Plus className="w-3.5 h-3.5 text-primary-600" /> Add Custom Component:
                </span>
                <input
                  type="text"
                  placeholder="Component Name"
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
                  <option value="Additional Component">Additional Component</option>
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
                      placeholder="%"
                      value={newCompPercentage}
                      onChange={(e) => setNewCompPercentage(e.target.value === '' ? '' : Number(e.target.value))}
                      className="w-20 px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    />
                    <select
                      value={newCompParentId}
                      onChange={(e) => setNewCompParentId(e.target.value)}
                      className="px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      <option value="">-- Parent Component --</option>
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
                    className="w-32 px-2.5 py-1.5 text-xs rounded-lg border border-neutral-300 bg-white text-neutral-800 focus:outline-none focus:ring-1 focus:ring-primary-500"
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <GlassCard className="p-3.5 space-y-1">
              <span className="text-[11px] text-neutral-500 font-medium">Monthly Recurring Earnings</span>
              <div className="text-base font-bold text-neutral-900">
                {formatIndianCurrency(
                  earningsComponents.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-[11px] text-neutral-500">
                Monthly Payout: {formatIndianCurrency(
                  earningsComponents.reduce((acc, c) => acc + c.monthlyEquivalent, 0),
                  2
                )}
              </div>
            </GlassCard>

            <GlassCard className="p-3.5 space-y-1">
              <span className="text-[11px] text-neutral-500 font-medium">Employer Contributions</span>
              <div className="text-base font-bold text-emerald-700">
                {formatIndianCurrency(
                  employerContributions.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-[11px] text-neutral-500">
                {formatPercentage(
                  employerContributions.reduce((acc, c) => acc + c.newPercentageOfCTC, 0),
                  2
                )} of CTC
              </div>
            </GlassCard>

            <GlassCard className="p-3.5 space-y-1">
              <span className="text-[11px] text-neutral-500 font-medium">Annual Benefits (LTA/Gratuity)</span>
              <div className="text-base font-bold text-blue-700">
                {formatIndianCurrency(
                  annualBenefits.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-[11px] text-blue-600">
                Processed Annually
              </div>
            </GlassCard>

            <GlassCard className="p-3.5 space-y-1">
              <span className="text-[11px] text-neutral-500 font-medium">Additional Bonus & Charges</span>
              <div className="text-base font-bold text-purple-700">
                {formatIndianCurrency(
                  additionalItems.reduce((acc, c) => acc + c.newAmount, 0),
                  2
                )}
              </div>
              <div className="text-[11px] text-purple-600">
                Part of 100% CTC
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
