export type ComponentCategory =
  | 'Earning'
  | 'Employer Contribution'
  | 'Annual Benefit'
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
  | 'Annual Benefit';

export interface CTCComponentInput {
  id: string;
  name: string;
  category: ComponentCategory;
  calculationMethod?: CalculationMethod; // 'Flat', 'Percentage', 'Formula'
  percentageValue?: number; // e.g. 50 for 50%
  percentageDerivedFromComponentId?: string; // id of parent component
  percentageDerivedFrom?: string; // fallback name of parent component
  defaultFormula?: string; // e.g. "50% of BASIC"
  oldAmount: number; // Annual amount (directly input if Flat, or calculated if derived)
  notes?: string;
  isCustom?: boolean;
}

export type RevisionMethod = 'PERCENTAGE' | 'TARGET_CTC';

export interface CTCCalculatorState {
  oldCTC: number; // Complete Old Annual CTC
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
  oldAmount: number; // Old Annual
  oldPercentageOfCTC: number; // e.g. 40.0 for 40%
  newAmount: number; // New Annual
  newPercentageOfCTC: number; // Percentage against New CTC
  monthlyEquivalent: number; // Annual / 12
  isAnnualPayout: boolean; // true for LTA, Gratuity, etc. (paid annually, not ordinary monthly cash payout)
  difference: number; // newAmount - oldAmount
  notes?: string;
  isCustom?: boolean;
  isFormulaDerived: boolean;
  dependencyNames?: string[];
  evaluationError?: string;
}

export interface CTCCalculationSummary {
  oldEnteredCTC: number;
  totalOldComponents: number;
  isOldSumMismatch: boolean;
  oldSumDifference: number; // totalOldComponents - oldEnteredCTC
  oldComponentsPercentageSum: number; // Sum of all old percentages (100% when balanced)

  calculatedNewCTC: number; // The target or calculated New CTC
  totalNewComponents: number;
  isNewSumMismatch: boolean;
  newSumDifference: number; // totalNewComponents - calculatedNewCTC

  totalIncrement: number; // calculatedNewCTC - oldEnteredCTC
  incrementPercentage: number; // % increase in CTC

  results: CTCComponentResult[];
  employeeDeductionResults?: CTCComponentResult[];
  calculationWarnings?: string[];
}

/**
 * Default components representing standard HRMS CTC components:
 * - Earnings: Direct (Basic, Conveyance, Other Earnings) and Formula-Derived (HRA = 50% of Basic)
 * - Employer Contributions: Employer PF, Employer Pension
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
    oldAmount: 120000,
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
    id: 'employer_pension',
    name: 'Employer Pension / EPS',
    category: 'Employer Contribution',
    calculationMethod: 'Flat',
    oldAmount: 7200,
    notes: 'Employer Pension Scheme / EPS contribution (Part of CTC)'
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
    oldAmount: 30000,
    notes: 'Statutory / Company Gratuity accrual - Annual component'
  }
];

/**
 * Separate Employee Deductions (distinct from Employer CTC cost).
 * Note: Employee PF is deducted from employee gross salary, NOT an additional employer cost on top of CTC.
 */
export const DEFAULT_EMPLOYEE_DEDUCTIONS: CTCComponentInput[] = [
  {
    id: 'employee_pf',
    name: 'Employee PF (PFEMP)',
    category: 'Employee Deduction',
    calculationMethod: 'Flat',
    oldAmount: 28800,
    notes: 'Deducted from employee salary (Not an employer-side CTC cost)'
  }
];

/**
 * Helper to classify component category and annual payout from name.
 */
export function classifyComponent(name: string): { category: ComponentCategory; isAnnualPayout: boolean } {
  const norm = (name || '').toLowerCase();
  if (norm.includes('lta') || norm.includes('leave travel') || norm.includes('gratuity') || norm.includes('bonus') || norm.includes('annual')) {
    return { category: 'Annual Benefit', isAnnualPayout: true };
  }
  if (norm.includes('employer') || norm.includes('epempr') || norm.includes('epsempr')) {
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
 *
 * Resolves parent components before dependent components.
 * Detects circular dependencies and identifies missing dependencies.
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
      amount: Number(comp.oldAmount) || 0,
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
    // Check fallback to Basic
    const basicComp = Array.from(compById.values()).find(c => c.name.trim().toLowerCase() === 'basic');
    if (basicComp && !comp.percentageDerivedFromComponentId && !comp.percentageDerivedFrom) {
      parentComp = basicComp;
      parentId = basicComp.id;
    }
  }

  if (!parentComp || !parentId) {
    const identifier = comp.percentageDerivedFromComponentId || comp.percentageDerivedFrom || 'Unknown';
    return {
      amount: Number(comp.oldAmount) || 0, // Fallback to entered amount if any
      formulaDescription: comp.defaultFormula || `Derived from ${identifier}`,
      error: `Missing parent dependency: ${identifier}`
    };
  }

  const parentAmount = resolvedAmounts.get(parentId) ?? (Number(parentComp.oldAmount) || 0);
  const percentage = Number(comp.percentageValue) || 0;
  const calculatedAmount = parentAmount * (percentage / 100);

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
  if (comp.category === 'Employer Contribution') {
    return 'Employer Contribution';
  }
  if (comp.category === 'Annual Benefit') {
    return 'Annual Benefit';
  }
  if (comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula') {
    return 'Formula Derived';
  }
  return 'Direct Input';
}

/**
 * Core CTC Revision Calculation Engine.
 *
 * Implements dependency-aware formula evaluation and strict CTC reconciliation:
 * 1. Resolves dependencies using Kahn's algorithm (topological sort).
 * 2. Evaluates formula-derived old amounts from parent values.
 * 3. Calculates complete Old Annual CTC and component percentages:
 *    Component Percentage = (Old Annual Component Amount / Old Annual CTC) * 100
 * 4. Determines New CTC via Increment Percentage or Target New CTC.
 * 5. Calculates revised component amounts:
 *    - Base / direct components scale proportionally with the revised CTC:
 *      New Annual Amount = New CTC * (Component Percentage / 100)
 *    - Formula-derived components calculate their revised values from their revised parent dependencies:
 *      New Annual Amount = Revised Parent Amount * (Percentage / 100)
 *    Mathematically, both produce identical, coherent results when parent scales by (New CTC / Old CTC),
 *    while preserving both formula relationships and total CTC reconciliation!
 * 6. Validates Old & New CTC reconciliation and highlights any discrepancies.
 */
export function calculateCTCRevision(state: CTCCalculatorState): CTCCalculationSummary {
  const {
    oldCTC,
    revisionMethod,
    incrementPercentage,
    targetCTC,
    components,
    employeeDeductions = []
  } = state;

  const calculationWarnings: string[] = [];

  // 1. Dependency Resolution
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

  // 2. Evaluate Old Amounts for all components in topological order
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
      const amt = Number(comp.oldAmount) || 0;
      resolvedOldAmounts.set(cid, amt);
      formulaDescriptions.set(cid, 'Direct Input');
    }
  }

  // 3. Determine New CTC
  let calculatedNewCTC = 0;
  if (revisionMethod === 'PERCENTAGE') {
    if (oldCTC > 0) {
      calculatedNewCTC = oldCTC * (1 + (incrementPercentage || 0) / 100);
    } else {
      calculatedNewCTC = 0;
    }
  } else {
    calculatedNewCTC = targetCTC || 0;
  }

  // 4. Compute revised amounts for all components in topological order
  const resolvedNewAmounts = new Map<string, number>();

  for (const cid of sortedIds) {
    const comp = compById.get(cid);
    if (!comp) continue;

    const isFormula = comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula';
    const oldAmt = resolvedOldAmounts.get(cid) ?? 0;
    const oldPercentageOfCTC = oldCTC > 0 ? (oldAmt / oldCTC) * 100 : 0;

    let newAmt = 0;
    if (isFormula) {
      // Find parent component id
      let parentId = comp.percentageDerivedFromComponentId;
      if (!parentId || !compById.has(parentId)) {
        const pName = (comp.percentageDerivedFrom || '').trim().toLowerCase();
        if (pName && compByName.has(pName)) {
          parentId = compByName.get(pName)!.id;
        } else {
          const basicComp = components.find(c => c.name.trim().toLowerCase() === 'basic');
          if (basicComp && !comp.percentageDerivedFromComponentId && !comp.percentageDerivedFrom) {
            parentId = basicComp.id;
          }
        }
      }

      if (parentId && resolvedNewAmounts.has(parentId)) {
        const revisedParentAmount = resolvedNewAmounts.get(parentId)!;
        const perc = Number(comp.percentageValue) || 0;
        newAmt = revisedParentAmount * (perc / 100);
      } else {
        // Fallback to proportional allocation if parent missing
        newAmt = oldCTC > 0 ? calculatedNewCTC * (oldPercentageOfCTC / 100) : 0;
      }
    } else {
      // Directly entered component: scales proportionally
      newAmt = oldCTC > 0 ? calculatedNewCTC * (oldPercentageOfCTC / 100) : 0;
    }

    resolvedNewAmounts.set(cid, newAmt);
  }

  let totalOldComponents = 0;
  let totalNewComponents = 0;
  let oldComponentsPercentageSum = 0;

  // 5. Build final component results preserving original list order
  const results: CTCComponentResult[] = components.map((comp) => {
    const oldAmount = resolvedOldAmounts.get(comp.id) ?? (Number(comp.oldAmount) || 0);
    totalOldComponents += oldAmount;

    // Component Percentage = (Old Annual Component Amount / Old Annual CTC) * 100
    const oldPercentageOfCTC = oldCTC > 0 ? (oldAmount / oldCTC) * 100 : 0;
    oldComponentsPercentageSum += oldPercentageOfCTC;

    const newAmount = resolvedNewAmounts.get(comp.id) ?? 0;
    totalNewComponents += newAmount;

    // New CTC %
    const newPercentageOfCTC = calculatedNewCTC > 0 ? (newAmount / calculatedNewCTC) * 100 : oldPercentageOfCTC;

    const difference = newAmount - oldAmount;
    const monthlyEquivalent = newAmount / 12;

    const isAnnualPayout =
      comp.category === 'Annual Benefit' ||
      classifyComponent(comp.name).isAnnualPayout;

    const isFormula = comp.calculationMethod === 'Percentage' || comp.calculationMethod === 'Formula';
    const displayCalculationMethod = getDisplayCalculationMethod(comp);
    const formulaDescription = formulaDescriptions.get(comp.id) || (isFormula ? (comp.defaultFormula || 'Formula Derived') : 'Direct Input');

    let dependencyNames: string[] | undefined;
    if (isFormula) {
      const pId = comp.percentageDerivedFromComponentId;
      const parent = pId ? compById.get(pId) : (comp.percentageDerivedFrom ? compByName.get(comp.percentageDerivedFrom.toLowerCase()) : undefined);
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
      oldPercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout,
      difference,
      notes: comp.notes,
      isCustom: comp.isCustom,
      isFormulaDerived: isFormula,
      dependencyNames,
      evaluationError: evaluationErrors.get(comp.id)
    };
  });

  // Calculate separate employee deductions if provided
  const employeeDeductionResults: CTCComponentResult[] = employeeDeductions.map((ded) => {
    const oldAmount = Number(ded.oldAmount) || 0;
    const oldPercentageOfCTC = oldCTC > 0 ? (oldAmount / oldCTC) * 100 : 0;
    const newAmount = oldCTC > 0 ? calculatedNewCTC * (oldPercentageOfCTC / 100) : 0;
    const newPercentageOfCTC = calculatedNewCTC > 0 ? (newAmount / calculatedNewCTC) * 100 : oldPercentageOfCTC;
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
      oldPercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout: false,
      difference,
      notes: ded.notes,
      isCustom: ded.isCustom,
      isFormulaDerived: false
    };
  });

  // 6. Summaries & Mismatches
  const isOldSumMismatch = Math.abs(totalOldComponents - oldCTC) > 0.01;
  const oldSumDifference = totalOldComponents - oldCTC;

  const isNewSumMismatch = Math.abs(totalNewComponents - calculatedNewCTC) > 0.01;
  const newSumDifference = totalNewComponents - calculatedNewCTC;

  const totalIncrement = calculatedNewCTC - oldCTC;
  const actualIncrementPct = oldCTC > 0 ? ((calculatedNewCTC - oldCTC) / oldCTC) * 100 : 0;

  return {
    oldEnteredCTC: oldCTC,
    totalOldComponents,
    isOldSumMismatch,
    oldSumDifference,
    oldComponentsPercentageSum,
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
