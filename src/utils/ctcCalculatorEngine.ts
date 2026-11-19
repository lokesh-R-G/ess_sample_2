export type ComponentCategory =
  | 'Earning'
  | 'Employer Contribution'
  | 'Annual Benefit'
  | 'Additional Component'
  | 'Other CTC Component'
  | 'Employee Deduction';

export type CalculationMethod =
  | 'Flat'
  | 'Percentage'
  | 'Formula';

export type DisplayCalculationMethod =
  | 'Direct Input'
  | 'Formula Derived'
  | 'Employer Contribution'
  | 'Annual Benefit'
  | 'Additional Bonus'
  | 'Additional Charges'
  | 'Additional CTC Component';

export interface CTCComponentInput {
  id: string;
  name: string;
  category: ComponentCategory;
  calculationMethod?: CalculationMethod; // 'Flat', 'Percentage', 'Formula'
  percentageValue?: number; // e.g. 50 for 50%
  percentageDerivedFromComponentId?: string; // id of parent component
  percentageDerivedFrom?: string; // fallback name of parent component
  defaultFormula?: string; // e.g. "50% of BASIC"
  oldAmount: number; // Annual amount in existing structure
  notes?: string;
  isCustom?: boolean;
}

export type RevisionMethod = 'PERCENTAGE' | 'TARGET_CTC';

export interface CTCCalculatorState {
  existingAnnualCTC: number; // Stored / fetched old annual CTC
  additionalBonus: number; // Additional Bonus to incorporate into baseline CTC
  additionalCharges: number; // Additional Charges to incorporate into baseline CTC
  additionalComponents?: CTCComponentInput[]; // Other additional components
  revisionMethod: RevisionMethod;
  incrementPercentage: number;
  targetCTC: number;
  components: CTCComponentInput[];
  employeeDeductions?: CTCComponentInput[]; // Separate employee deductions for reference
}

export interface CTCComponentResult {
  id: string;
  name: string;
  category: ComponentCategory;
  calculationMethod: CalculationMethod;
  displayCalculationMethod: DisplayCalculationMethod;
  formulaDescription: string;
  percentageValue?: number;
  percentageDerivedFromComponentId?: string;
  oldAmount: number; // Old Annual amount
  baselineAmount: number; // Updated Baseline Amount (incorporating additional bonus/charges)
  baselinePercentageOfCTC: number; // (baselineAmount / updatedBaselineCTC) * 100
  newAmount: number; // New Annual amount
  newPercentageOfCTC: number; // (newAmount / calculatedNewCTC) * 100
  monthlyEquivalent: number; // Annual / 12
  isAnnualPayout: boolean; // true for LTA, Gratuity, Bonus, etc.
  difference: number; // newAmount - baselineAmount
  notes?: string;
  isCustom?: boolean;
  isFormulaDerived: boolean;
  isAdditional?: boolean;
  dependencyNames?: string[];
  evaluationError?: string;
}

export interface CTCCalculationSummary {
  existingAnnualCTC: number; // Old annual CTC
  totalExistingComponents: number; // Sum of existing component amounts
  isExistingMismatch: boolean; // Math.abs(totalExistingComponents - existingAnnualCTC) > 0.01
  existingMismatchDifference: number; // totalExistingComponents - existingAnnualCTC

  additionalBonus: number;
  additionalCharges: number;
  totalAdditionalAmount: number; // additionalBonus + additionalCharges + additionalComponents

  updatedBaselineCTC: number; // Complete baseline CTC = totalExistingComponents + totalAdditionalAmount
  totalBaselineComponents: number;
  baselineComponentsPercentageSum: number; // Must total 100%

  calculatedNewCTC: number; // Target or Increment New CTC
  totalNewComponents: number;
  isNewSumMismatch: boolean;
  newSumDifference: number; // totalNewComponents - calculatedNewCTC

  totalIncrement: number; // calculatedNewCTC - updatedBaselineCTC
  incrementPercentage: number; // % increase over updatedBaselineCTC

  results: CTCComponentResult[];
  employeeDeductionResults?: CTCComponentResult[];
  calculationWarnings?: string[];
}

/**
 * Standard illustrative CTC components used for default preview:
 * - Earnings: Basic, HRA (50% of Basic), Conveyance, Other Earnings
 * - Employer Contributions: Employer PF, Employer ESI
 * - Annual Benefits: LTA, Gratuity
 */
export const DEFAULT_EXAMPLE_COMPONENTS: CTCComponentInput[] = [
  {
    id: 'basic',
    name: 'Basic',
    category: 'Earning',
    calculationMethod: 'Flat',
    oldAmount: 240000,
    notes: 'Monthly recurring basic salary component (Direct Input)'
  },
  {
    id: 'hra',
    name: 'HRA',
    category: 'Earning',
    calculationMethod: 'Percentage',
    percentageValue: 50,
    percentageDerivedFromComponentId: 'basic',
    defaultFormula: '50% of Basic',
    oldAmount: 120000,
    notes: 'House Rent Allowance (50% of Basic)'
  },
  {
    id: 'conveyance',
    name: 'Conveyance',
    category: 'Earning',
    calculationMethod: 'Flat',
    oldAmount: 30000,
    notes: 'Conveyance / Transport Allowance (Direct Input)'
  },
  {
    id: 'other_earnings',
    name: 'Other Earnings',
    category: 'Earning',
    calculationMethod: 'Flat',
    oldAmount: 90000,
    notes: 'Special Allowance / Medical / Other Earnings (Direct Input)'
  },
  {
    id: 'employer_pf',
    name: 'Employer PF',
    category: 'Employer Contribution',
    calculationMethod: 'Flat',
    oldAmount: 28800,
    notes: 'Employer Provident Fund contribution (Part of CTC)'
  },
  {
    id: 'employer_esi',
    name: 'Employer ESI',
    category: 'Employer Contribution',
    calculationMethod: 'Flat',
    oldAmount: 7200,
    notes: 'Employer ESI Contribution (Part of CTC)'
  },
  {
    id: 'lta',
    name: 'LTA',
    category: 'Annual Benefit',
    calculationMethod: 'Flat',
    oldAmount: 24000,
    notes: 'Leave Travel Allowance - Annual benefit (paid annually)'
  },
  {
    id: 'gratuity',
    name: 'Gratuity',
    category: 'Annual Benefit',
    calculationMethod: 'Flat',
    oldAmount: 20000,
    notes: 'Statutory / Company Gratuity accrual - Annual component'
  }
];

/**
 * Separate Employee Deductions (distinct from Employer CTC cost).
 * Note: Employee PF and Employee ESI are deducted from employee gross salary, NOT an employer cost.
 */
export const DEFAULT_EMPLOYEE_DEDUCTIONS: CTCComponentInput[] = [
  {
    id: 'employee_pf',
    name: 'Employee PF (PFEMP)',
    category: 'Employee Deduction',
    calculationMethod: 'Flat',
    oldAmount: 28800,
    notes: 'Deducted from employee salary (Not an employer-side CTC cost)'
  },
  {
    id: 'employee_esi',
    name: 'Employee ESI',
    category: 'Employee Deduction',
    calculationMethod: 'Flat',
    oldAmount: 4500,
    notes: 'Deducted from employee salary (Not an employer-side CTC cost)'
  }
];

/**
 * Helper to classify component category and annual payout from name.
 */
export function classifyComponent(name: string): { category: ComponentCategory; isAnnualPayout: boolean } {
  const norm = (name || '').toLowerCase();
  if (norm.includes('bonus') || norm.includes('charge')) {
    return { category: 'Additional Component', isAnnualPayout: true };
  }
  if (norm.includes('lta') || norm.includes('leave travel') || norm.includes('gratuity') || norm.includes('annual')) {
    return { category: 'Annual Benefit', isAnnualPayout: true };
  }
  if (
    norm.includes('employer') ||
    norm.includes('epempr') ||
    norm.includes('epsempr') ||
    norm.includes('pf admin') ||
    norm.includes('edli')
  ) {
    return { category: 'Employer Contribution', isAnnualPayout: false };
  }
  if (norm.includes('deduction') || (norm.includes('employee') && norm.includes('pf')) || norm.includes('pfemp')) {
    return { category: 'Employee Deduction', isAnnualPayout: false };
  }
  return { category: 'Earning', isAnnualPayout: false };
}

/**
 * Formats a number in Indian currency style (e.g., ₹2,40,000.00).
 */
export function formatIndianCurrency(amount: number, decimals: number = 2): string {
  if (isNaN(amount) || amount === null || amount === undefined) {
    return '₹0.00';
  }
  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);

  const formatted = absAmount.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return `${isNegative ? '-' : ''}₹${formatted}`;
}

/**
 * Formats percentage display.
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  if (isNaN(value) || value === null || value === undefined) {
    return '0.00%';
  }
  return `${value.toFixed(decimals)}%`;
}

/**
 * Topological Sort & Dependency Resolution Engine for Salary Components.
 * Uses Kahn's algorithm matching backend SalaryCalculationEngine.
 */
export interface DependencyResolutionResult {
  sortedIds: string[];
  circularError?: string;
  missingDependencies: Record<string, string>; // childId -> parent identifier
}

export function resolveComponentDependencies(components: CTCComponentInput[]): DependencyResolutionResult {
  const compById = new Map<string, CTCComponentInput>();
  const compByName = new Map<string, CTCComponentInput>();

  for (const c of components) {
    compById.set(c.id, c);
    compByName.set(c.name.trim().toLowerCase(), c);
  }

  const inDegree = new Map<string, number>();
  const adjList = new Map<string, string[]>(); // parentId -> [childId]
  const missingDependencies: Record<string, string> = {};

  for (const c of components) {
    inDegree.set(c.id, 0);
    adjList.set(c.id, []);
  }

  for (const c of components) {
    const isFormula = c.calculationMethod === 'Percentage' || c.calculationMethod === 'Formula';
    if (isFormula) {
      let parentId = c.percentageDerivedFromComponentId;
      if (!parentId || !compById.has(parentId)) {
        // Fallback by name
        const pName = (c.percentageDerivedFrom || '').trim().toLowerCase();
        if (pName && compByName.has(pName)) {
          parentId = compByName.get(pName)!.id;
        } else {
          // Check if there is a Basic component as canonical fallback
          const basicComp = components.find(comp => comp.name.trim().toLowerCase() === 'basic');
          if (basicComp && !c.percentageDerivedFromComponentId && !c.percentageDerivedFrom) {
            parentId = basicComp.id;
          }
        }
      }

      if (parentId && compById.has(parentId)) {
        adjList.get(parentId)!.push(c.id);
        inDegree.set(c.id, (inDegree.get(c.id) || 0) + 1);
      } else {
        const identifier = c.percentageDerivedFromComponentId || c.percentageDerivedFrom || 'Unknown Parent';
        missingDependencies[c.id] = identifier;
      }
    }
  }

  // Kahn's algorithm
  const queue: string[] = [];
  for (const [id, deg] of inDegree.entries()) {
    if (deg === 0) {
      queue.push(id);
    }
  }

  const sortedIds: string[] = [];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    sortedIds.push(curr);

    const neighbors = adjList.get(curr) || [];
    for (const neighbor of neighbors) {
      const nextDeg = (inDegree.get(neighbor) || 1) - 1;
      inDegree.set(neighbor, nextDeg);
      if (nextDeg === 0) {
        queue.push(neighbor);
      }
    }
  }

  let circularError: string | undefined;
  if (sortedIds.length !== components.length) {
    const unvisited = components.filter(c => !sortedIds.includes(c.id)).map(c => c.name);
    circularError = `Circular dependency detected involving component(s): ${unvisited.join(', ')}`;
    // Append unvisited to prevent crashing downstream display
    for (const c of components) {
      if (!sortedIds.includes(c.id)) {
        sortedIds.push(c.id);
      }
    }
  }

  return {
    sortedIds,
    circularError,
    missingDependencies
  };
}

/**
 * Evaluates a single formula-derived component's annual amount from parent component values.
 */
export function evaluateComponentFormula(
  comp: CTCComponentInput,
  compById: Map<string, CTCComponentInput>,
  compByName: Map<string, CTCComponentInput>,
  resolvedAmounts: Map<string, number>
): { amount: number; formulaDescription: string; error?: string } {
  const isFormula = comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula';
  if (!isFormula) {
    return {
      amount: Math.max(0, Number(comp.oldAmount) || 0),
      formulaDescription: 'Direct Input'
    };
  }

  let parentId = comp.percentageDerivedFromComponentId;
  let parentComp: CTCComponentInput | undefined;

  if (parentId && compById.has(parentId)) {
    parentComp = compById.get(parentId);
  } else if (comp.percentageDerivedFrom) {
    const pName = comp.percentageDerivedFrom.trim().toLowerCase();
    if (compByName.has(pName)) {
      parentComp = compByName.get(pName);
      parentId = parentComp?.id;
    }
  }

  if (!parentComp) {
    const basicComp = Array.from(compById.values()).find(c => c.name.trim().toLowerCase() === 'basic');
    if (basicComp && !comp.percentageDerivedFromComponentId && !comp.percentageDerivedFrom) {
      parentComp = basicComp;
      parentId = basicComp.id;
    }
  }

  if (!parentComp || !parentId) {
    const identifier = comp.percentageDerivedFromComponentId || comp.percentageDerivedFrom || 'Unknown';
    return {
      amount: Math.max(0, Number(comp.oldAmount) || 0),
      formulaDescription: comp.defaultFormula || `Derived from ${identifier}`,
      error: `Missing parent dependency: ${identifier}`
    };
  }

  const parentAmount = resolvedAmounts.get(parentId) ?? (Math.max(0, Number(parentComp.oldAmount) || 0));
  const percentage = Number(comp.percentageValue) || 0;
  const calculatedAmount = Math.max(0, parentAmount * (percentage / 100));

  const formulaDescription = comp.defaultFormula || `${percentage}% of ${parentComp.name}`;

  return {
    amount: calculatedAmount,
    formulaDescription
  };
}

/**
 * Determine the Display Calculation Method for a component.
 */
export function getDisplayCalculationMethod(
  comp: CTCComponentInput
): DisplayCalculationMethod {
  if (comp.id === 'addl_bonus' || comp.name.toLowerCase().includes('bonus')) {
    return 'Additional Bonus';
  }
  if (comp.id === 'addl_charges' || comp.name.toLowerCase().includes('charge')) {
    return 'Additional Charges';
  }
  if (comp.category === 'Employer Contribution') {
    return 'Employer Contribution';
  }
  if (comp.category === 'Annual Benefit') {
    return 'Annual Benefit';
  }
  if (comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula') {
    return 'Formula Derived';
  }
  if (comp.category === 'Additional Component') {
    return 'Additional CTC Component';
  }
  return 'Direct Input';
}

/**
 * Core CTC Revision Calculation Engine.
 *
 * Implements the mandated workflow:
 * 1. Resolves all existing salary components (direct & formula-derived).
 * 2. Incorporates Additional Bonus and Additional Charges into the Complete Baseline CTC.
 * 3. Recalculates the complete CTC percentage distribution against the updated Baseline CTC:
 *    Component Percentage = (Component Baseline Amount / Updated Baseline CTC) * 100
 *    Sum of component percentages equals 100.00%.
 * 4. Applies revision (Percentage Increment or Direct Target CTC):
 *    New Annual Component Amount = New CTC * (Component Percentage / 100)
 * 5. Strictly reconciles New Total Components with New Target CTC.
 */
export function calculateCTCRevision(state: CTCCalculatorState): CTCCalculationSummary {
  const {
    existingAnnualCTC = 0,
    additionalBonus = 0,
    additionalCharges = 0,
    additionalComponents = [],
    revisionMethod,
    incrementPercentage = 0,
    targetCTC = 0,
    components = [],
    employeeDeductions = []
  } = state;

  const calculationWarnings: string[] = [];

  // Reject negative additional amounts
  const safeBonus = Math.max(0, Number(additionalBonus) || 0);
  const safeCharges = Math.max(0, Number(additionalCharges) || 0);

  // 1. Dependency Resolution for existing components
  const { sortedIds, circularError, missingDependencies } = resolveComponentDependencies(components);
  if (circularError) {
    calculationWarnings.push(circularError);
  }
  for (const [childId, pIdentifier] of Object.entries(missingDependencies)) {
    const child = components.find(c => c.id === childId);
    calculationWarnings.push(`Component "${child?.name || childId}" depends on missing parent "${pIdentifier}".`);
  }

  const compById = new Map<string, CTCComponentInput>();
  const compByName = new Map<string, CTCComponentInput>();
  for (const c of components) {
    compById.set(c.id, c);
    compByName.set(c.name.trim().toLowerCase(), c);
  }

  // 2. Evaluate Old Amounts for existing components in topological order
  const resolvedOldAmounts = new Map<string, number>();
  const formulaDescriptions = new Map<string, string>();
  const evaluationErrors = new Map<string, string>();

  for (const cid of sortedIds) {
    const comp = compById.get(cid);
    if (!comp) continue;

    const isFormula = comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula';
    if (isFormula) {
      const evalRes = evaluateComponentFormula(comp, compById, compByName, resolvedOldAmounts);
      resolvedOldAmounts.set(cid, evalRes.amount);
      formulaDescriptions.set(cid, evalRes.formulaDescription);
      if (evalRes.error) {
        evaluationErrors.set(cid, evalRes.error);
      }
    } else {
      const amt = Math.max(0, Number(comp.oldAmount) || 0);
      resolvedOldAmounts.set(cid, amt);
      formulaDescriptions.set(cid, 'Direct Input');
    }
  }

  let totalExistingComponents = 0;
  for (const comp of components) {
    totalExistingComponents += resolvedOldAmounts.get(comp.id) ?? 0;
  }

  // Check mismatch between existing stored CTC and sum of existing components
  const isExistingMismatch = existingAnnualCTC > 0 && Math.abs(totalExistingComponents - existingAnnualCTC) > 0.01;
  const existingMismatchDifference = totalExistingComponents - existingAnnualCTC;
  if (isExistingMismatch) {
    calculationWarnings.push(
      `Existing salary components sum (${formatIndianCurrency(totalExistingComponents, 2)}) differs from stored annual CTC (${formatIndianCurrency(existingAnnualCTC, 2)}).`
    );
  }

  // 3. Assemble complete list of baseline components (Existing + Additional Bonus + Additional Charges + Other Additionals)
  const allBaselineComponents: CTCComponentInput[] = [...components];

  if (safeBonus > 0) {
    allBaselineComponents.push({
      id: 'addl_bonus',
      name: 'Additional Bonus',
      category: 'Additional Component',
      calculationMethod: 'Flat',
      oldAmount: 0,
      notes: 'Additional annual bonus incorporated into baseline CTC'
    });
    resolvedOldAmounts.set('addl_bonus', 0);
    formulaDescriptions.set('addl_bonus', 'Direct Input');
  }

  if (safeCharges > 0) {
    allBaselineComponents.push({
      id: 'addl_charges',
      name: 'Additional Charges',
      category: 'Additional Component',
      calculationMethod: 'Flat',
      oldAmount: 0,
      notes: 'Additional employer charges incorporated into baseline CTC'
    });
    resolvedOldAmounts.set('addl_charges', 0);
    formulaDescriptions.set('addl_charges', 'Direct Input');
  }

  for (const addl of additionalComponents) {
    const safeAmt = Math.max(0, Number(addl.oldAmount) || 0);
    allBaselineComponents.push({
      ...addl,
      category: addl.category || 'Additional Component',
      calculationMethod: 'Flat',
      oldAmount: 0
    });
    resolvedOldAmounts.set(addl.id, 0);
    formulaDescriptions.set(addl.id, 'Direct Input');
  }

  // Baseline amounts: for existing components, it's resolvedOldAmounts; for bonus/charges, it's safeBonus/safeCharges
  const baselineAmounts = new Map<string, number>();
  for (const c of components) {
    baselineAmounts.set(c.id, resolvedOldAmounts.get(c.id) ?? 0);
  }
  if (safeBonus > 0) {
    baselineAmounts.set('addl_bonus', safeBonus);
  }
  if (safeCharges > 0) {
    baselineAmounts.set('addl_charges', safeCharges);
  }
  for (const addl of additionalComponents) {
    baselineAmounts.set(addl.id, Math.max(0, Number(addl.oldAmount) || 0));
  }

  const extraAdditionalAmount = additionalComponents.reduce((sum, c) => sum + Math.max(0, Number(c.oldAmount) || 0), 0);
  const totalAdditionalAmount = safeBonus + safeCharges + extraAdditionalAmount;

  // Complete Baseline CTC includes existing components total + additional bonus + additional charges
  const updatedBaselineCTC = totalExistingComponents + totalAdditionalAmount;

  // 4. Recalculate Percentage Distribution for EVERY included component against updatedBaselineCTC
  let baselineComponentsPercentageSum = 0;
  const baselinePercentages = new Map<string, number>();

  for (const c of allBaselineComponents) {
    const bAmt = baselineAmounts.get(c.id) ?? 0;
    const pct = updatedBaselineCTC > 0 ? (bAmt / updatedBaselineCTC) * 100 : 0;
    baselinePercentages.set(c.id, pct);
    baselineComponentsPercentageSum += pct;
  }

  // 5. Determine New CTC
  let calculatedNewCTC = 0;
  if (revisionMethod === 'PERCENTAGE') {
    if (updatedBaselineCTC > 0) {
      calculatedNewCTC = updatedBaselineCTC * (1 + (incrementPercentage || 0) / 100);
    } else {
      calculatedNewCTC = 0;
    }
  } else {
    calculatedNewCTC = Math.max(0, Number(targetCTC) || 0);
  }

  // 6. Calculate New Component Amounts using Recalculated Component Percentages
  let totalNewComponents = 0;
  const results: CTCComponentResult[] = allBaselineComponents.map((comp) => {
    const oldAmount = resolvedOldAmounts.get(comp.id) ?? 0;
    const baselineAmount = baselineAmounts.get(comp.id) ?? 0;
    const baselinePercentageOfCTC = baselinePercentages.get(comp.id) ?? 0;

    // New Annual Component Amount = New CTC * (Component Percentage / 100)
    const newAmount = updatedBaselineCTC > 0 ? calculatedNewCTC * (baselinePercentageOfCTC / 100) : 0;
    totalNewComponents += newAmount;

    const newPercentageOfCTC = calculatedNewCTC > 0 ? (newAmount / calculatedNewCTC) * 100 : baselinePercentageOfCTC;
    const difference = newAmount - baselineAmount;
    const monthlyEquivalent = newAmount / 12;

    const isAdditional = comp.id === 'addl_bonus' || comp.id === 'addl_charges' || comp.category === 'Additional Component';
    const isAnnualPayout =
      isAdditional ||
      comp.category === 'Annual Benefit' ||
      classifyComponent(comp.name).isAnnualPayout;

    const isFormula = comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula';
    const displayCalculationMethod = getDisplayCalculationMethod(comp);
    const formulaDescription =
      formulaDescriptions.get(comp.id) ||
      (isFormula ? (comp.defaultFormula || 'Formula Derived') : 'Direct Input');

    let dependencyNames: string[] | undefined;
    if (isFormula) {
      const pId = comp.percentageDerivedFromComponentId;
      const parent = pId
        ? compById.get(pId)
        : comp.percentageDerivedFrom
        ? compByName.get(comp.percentageDerivedFrom.toLowerCase())
        : undefined;
      if (parent) {
        dependencyNames = [parent.name];
      }
    }

    return {
      id: comp.id,
      name: comp.name,
      category: comp.category,
      calculationMethod: comp.calculationMethod || 'Flat',
      displayCalculationMethod,
      formulaDescription,
      percentageValue: comp.percentageValue,
      percentageDerivedFromComponentId: comp.percentageDerivedFromComponentId,
      oldAmount,
      baselineAmount,
      baselinePercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout,
      difference,
      notes: comp.notes,
      isCustom: comp.isCustom,
      isFormulaDerived: isFormula,
      isAdditional,
      dependencyNames,
      evaluationError: evaluationErrors.get(comp.id)
    };
  });

  // Calculate separate employee deductions if provided
  const employeeDeductionResults: CTCComponentResult[] = employeeDeductions.map((ded) => {
    const oldAmount = Math.max(0, Number(ded.oldAmount) || 0);
    const baselinePercentageOfCTC = updatedBaselineCTC > 0 ? (oldAmount / updatedBaselineCTC) * 100 : 0;
    const newAmount = updatedBaselineCTC > 0 ? calculatedNewCTC * (baselinePercentageOfCTC / 100) : 0;
    const newPercentageOfCTC = calculatedNewCTC > 0 ? (newAmount / calculatedNewCTC) * 100 : baselinePercentageOfCTC;
    const difference = newAmount - oldAmount;
    const monthlyEquivalent = newAmount / 12;

    return {
      id: ded.id,
      name: ded.name,
      category: 'Employee Deduction',
      calculationMethod: 'Flat',
      displayCalculationMethod: 'Direct Input',
      formulaDescription: 'Direct Input',
      oldAmount,
      baselineAmount: oldAmount,
      baselinePercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout: false,
      difference,
      notes: ded.notes,
      isCustom: ded.isCustom,
      isFormulaDerived: false,
      isAdditional: false
    };
  });

  // 7. Summaries & Reconciliation
  const isNewSumMismatch = Math.abs(totalNewComponents - calculatedNewCTC) > 0.01;
  const newSumDifference = totalNewComponents - calculatedNewCTC;

  const totalIncrement = calculatedNewCTC - updatedBaselineCTC;
  const actualIncrementPct = updatedBaselineCTC > 0 ? ((calculatedNewCTC - updatedBaselineCTC) / updatedBaselineCTC) * 100 : 0;

  return {
    existingAnnualCTC,
    totalExistingComponents,
    isExistingMismatch,
    existingMismatchDifference,

    additionalBonus: safeBonus,
    additionalCharges: safeCharges,
    totalAdditionalAmount,

    updatedBaselineCTC,
    totalBaselineComponents: updatedBaselineCTC,
    baselineComponentsPercentageSum,

    calculatedNewCTC,
    totalNewComponents,
    isNewSumMismatch,
    newSumDifference,

    totalIncrement,
    incrementPercentage: actualIncrementPct,

    results,
    employeeDeductionResults,
    calculationWarnings: calculationWarnings.length > 0 ? calculationWarnings : undefined
  };
}
