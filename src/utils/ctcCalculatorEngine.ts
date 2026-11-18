export type ComponentCategory =
  | 'Earning'
  | 'Employer Contribution'
  | 'Annual Benefit'
  | 'Other CTC Component'
  | 'Employee Deduction';

export interface CTCComponentInput {
  id: string;
  name: string;
  category: ComponentCategory;
  oldAmount: number; // Annual amount
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
  oldAmount: number; // Old Annual
  oldPercentageOfCTC: number; // e.g. 40.0 for 40%
  newAmount: number; // New Annual
  newPercentageOfCTC: number; // Should match old percentage against New CTC
  monthlyEquivalent: number; // Annual / 12
  isAnnualPayout: boolean; // true for LTA, Gratuity, etc. (paid annually, not ordinary monthly cash payout)
  difference: number; // newAmount - oldAmount
  notes?: string;
  isCustom?: boolean;
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
}

/**
 * Default components representing the illustrative and standard CTC components:
 * - Earnings: Basic, HRA, Conveyance, Other Earnings / Medical
 * - Employer Contributions: Employer PF, Employer Pension
 * - Annual Benefits: LTA, Gratuity
 */
export const DEFAULT_EXAMPLE_COMPONENTS: CTCComponentInput[] = [
  {
    id: 'basic',
    name: 'Basic',
    category: 'Earning',
    oldAmount: 240000,
    notes: 'Monthly recurring basic salary component'
  },
  {
    id: 'hra',
    name: 'HRA',
    category: 'Earning',
    oldAmount: 120000,
    notes: 'House Rent Allowance'
  },
  {
    id: 'conveyance',
    name: 'Conveyance',
    category: 'Earning',
    oldAmount: 30000,
    notes: 'Conveyance / Transport Allowance'
  },
  {
    id: 'other_earnings',
    name: 'Other Earnings',
    category: 'Earning',
    oldAmount: 120000,
    notes: 'Special Allowance / Medical / Other Earnings'
  },
  {
    id: 'employer_pf',
    name: 'Employer PF',
    category: 'Employer Contribution',
    oldAmount: 28800,
    notes: 'Employer Provident Fund contribution (Part of CTC)'
  },
  {
    id: 'employer_pension',
    name: 'Employer Pension / EPS',
    category: 'Employer Contribution',
    oldAmount: 7200,
    notes: 'Employer Pension Scheme / EPS contribution (Part of CTC)'
  },
  {
    id: 'lta',
    name: 'LTA',
    category: 'Annual Benefit',
    oldAmount: 24000,
    notes: 'Leave Travel Allowance - Annual benefit (paid annually)'
  },
  {
    id: 'gratuity',
    name: 'Gratuity',
    category: 'Annual Benefit',
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
    oldAmount: 28800,
    notes: 'Deducted from employee salary (Not an employer-side CTC cost)'
  }
];

/**
 * Helper to classify component category from name or existing types.
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
 * Core CTC Revision Calculation Engine.
 *
 * Implements strict proportional calculation for EVERY component against complete CTC:
 *
 * 1. Component Percentage = (Old Annual Component Amount / Old Annual CTC) * 100
 * 2. New CTC = Old CTC * (1 + Increment % / 100)  OR  Direct Target CTC
 * 3. New Annual Component Amount = New Annual CTC * (Old Component Percentage / 100)
 *
 * NO component remains static. Employer PF, Employer Pension, LTA, and Gratuity all
 * participate proportionally in the complete CTC calculation.
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

  // 1. Determine New CTC
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

  let totalOldComponents = 0;
  let totalNewComponents = 0;
  let oldComponentsPercentageSum = 0;

  // 2. Compute component breakdown proportionally for EVERY included component
  const results: CTCComponentResult[] = components.map((comp) => {
    const oldAmount = Number(comp.oldAmount) || 0;
    totalOldComponents += oldAmount;

    // Component Percentage = (Old Annual Component Amount / Old Annual CTC) * 100
    const oldPercentageOfCTC = oldCTC > 0 ? (oldAmount / oldCTC) * 100 : 0;
    oldComponentsPercentageSum += oldPercentageOfCTC;

    // New Annual Component Amount = New Annual CTC * (Old Component Percentage / 100)
    // which is mathematically identical to (oldAmount / oldCTC) * calculatedNewCTC when oldCTC > 0
    const newAmount = oldCTC > 0 ? calculatedNewCTC * (oldPercentageOfCTC / 100) : 0;
    totalNewComponents += newAmount;

    // New CTC % (matches old percentage relative to new CTC)
    const newPercentageOfCTC = calculatedNewCTC > 0 ? (newAmount / calculatedNewCTC) * 100 : oldPercentageOfCTC;

    const difference = newAmount - oldAmount;
    const monthlyEquivalent = newAmount / 12;

    const isAnnualPayout =
      comp.category === 'Annual Benefit' ||
      classifyComponent(comp.name).isAnnualPayout;

    return {
      id: comp.id,
      name: comp.name,
      category: comp.category,
      oldAmount,
      oldPercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout,
      difference,
      notes: comp.notes,
      isCustom: comp.isCustom,
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
      oldAmount,
      oldPercentageOfCTC,
      newAmount,
      newPercentageOfCTC,
      monthlyEquivalent,
      isAnnualPayout: false,
      difference,
      notes: ded.notes,
      isCustom: ded.isCustom
    };
  });

  // 3. Summaries & Mismatches
  const isOldSumMismatch = Math.abs(totalOldComponents - oldCTC) > 0.01;
  const oldSumDifference = totalOldComponents - oldCTC;

  // Since all components are proportional, if sum(old) == oldCTC, then sum(new) == newCTC
  // If sum(old) != oldCTC, sum(new) differs from newCTC proportionately
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
    employeeDeductionResults
  };
}
