export interface CTCComponentInput {
  id: string;
  name: string;
  oldAmount: number;
  isStatic?: boolean; // Static PF components remain fixed
  notes?: string;
  isCustom?: boolean;
}

export type RevisionMethod = 'PERCENTAGE' | 'TARGET_CTC';

export interface CTCCalculatorState {
  oldCTC: number;
  revisionMethod: RevisionMethod;
  incrementPercentage: number;
  targetCTC: number;
  components: CTCComponentInput[];
}

export interface CTCComponentResult {
  id: string;
  name: string;
  oldAmount: number;
  oldPercentageOfCTC: number; // e.g. 0.45 or 45%
  isStatic: boolean;
  newAmount: number;
  difference: number;
  notes?: string;
  isCustom?: boolean;
}

export interface CTCCalculationSummary {
  oldEnteredCTC: number;
  totalOldComponents: number;
  isOldSumMismatch: boolean;
  oldSumDifference: number; // totalOldComponents - oldEnteredCTC

  calculatedNewCTC: number; // The target or calculated New CTC
  totalNewComponents: number;
  isNewSumMismatch: boolean;
  newSumDifference: number; // totalNewComponents - calculatedNewCTC

  totalComponentIncrease: number; // totalNewComponents - totalOldComponents
  actualPercentageIncrease: number; // (totalComponentIncrease / totalOldComponents) * 100 or on CTC
  ctcPercentageIncrease: number; // (calculatedNewCTC - oldEnteredCTC) / oldEnteredCTC * 100

  results: CTCComponentResult[];
}

export const DEFAULT_EXCEL_COMPONENTS: CTCComponentInput[] = [
  { id: 'basic', name: 'Basic', oldAmount: 630000, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'hra', name: 'HRA', oldAmount: 315000, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'conveyance', name: 'Conveyance', oldAmount: 96000, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'medical', name: 'Medical', oldAmount: 84000, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'education', name: 'Education', oldAmount: 84000, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'refreshments', name: 'Refreshments', oldAmount: 32316, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'incentive', name: 'Incentive', oldAmount: 0, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'lta', name: 'LTA', oldAmount: 52500, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'bonus', name: 'Bonus', oldAmount: 52500, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'gratuity', name: 'Gratuity', oldAmount: 30288, isStatic: false, notes: 'Calculated using its share of old CTC' },
  { id: 'pf_employee', name: 'PF Employee (PFEMP)', oldAmount: 36000, isStatic: true, notes: 'Static: edit Old Amount to change the fixed PF value' },
  { id: 'pf_employer', name: 'PF Employer (EPEMPR)', oldAmount: 37800, isStatic: true, notes: 'Static: edit Old Amount to change the fixed PF value' },
  { id: 'eps_employer', name: 'EPS Employer (EPSEMPR)', oldAmount: 0, isStatic: true, notes: 'Static: edit Old Amount to change the fixed PF value' },
];

/**
 * Checks if a component is one of the designated static PF components.
 */
export function isStaticPFComponent(name: string, id?: string): boolean {
  const normalized = (name || id || '').toUpperCase();
  return (
    normalized.includes('PFEMP') ||
    normalized.includes('EPEMPR') ||
    normalized.includes('EPSEMPR') ||
    (normalized.includes('PF') && (normalized.includes('EMPLOYEE') || normalized.includes('EMPLOYER'))) ||
    normalized.includes('EPS')
  );
}

/**
 * Formats a number in Indian currency style (e.g., ₹10,79,996.91 or ₹10,79,997).
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
 * Pure, isolated, unit-testable and deterministic function reproducing Excel workbook behaviour.
 */
export function calculateCTCRevision(state: CTCCalculatorState): CTCCalculationSummary {
  const { oldCTC, revisionMethod, incrementPercentage, targetCTC, components } = state;

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

  // 2. Compute component breakdown
  const results: CTCComponentResult[] = components.map((comp) => {
    const oldAmount = Number(comp.oldAmount) || 0;
    totalOldComponents += oldAmount;

    // % of Old CTC = Old Component Amount / Old CTC
    const oldPercentageOfCTC = oldCTC > 0 ? oldAmount / oldCTC : 0;

    let newAmount = 0;
    if (comp.isStatic) {
      // For components marked PF Static = Yes: New Component Amount = Old Component Amount
      newAmount = oldAmount;
    } else {
      // For every non-static component: (Old Component Amount / Old CTC) * New CTC
      newAmount = oldCTC > 0 ? oldPercentageOfCTC * calculatedNewCTC : 0;
    }

    totalNewComponents += newAmount;
    const difference = newAmount - oldAmount;

    return {
      id: comp.id,
      name: comp.name,
      oldAmount,
      oldPercentageOfCTC,
      isStatic: !!comp.isStatic,
      newAmount,
      difference,
      notes: comp.notes,
      isCustom: comp.isCustom,
    };
  });

  // 3. Summaries & Differences
  const isOldSumMismatch = Math.abs(totalOldComponents - oldCTC) > 0.01;
  const oldSumDifference = totalOldComponents - oldCTC;

  const isNewSumMismatch = Math.abs(totalNewComponents - calculatedNewCTC) > 0.01;
  const newSumDifference = totalNewComponents - calculatedNewCTC;

  const totalComponentIncrease = totalNewComponents - totalOldComponents;
  const actualPercentageIncrease = totalOldComponents > 0 ? (totalComponentIncrease / totalOldComponents) * 100 : 0;
  const ctcPercentageIncrease = oldCTC > 0 ? ((calculatedNewCTC - oldCTC) / oldCTC) * 100 : 0;

  return {
    oldEnteredCTC: oldCTC,
    totalOldComponents,
    isOldSumMismatch,
    oldSumDifference,
    calculatedNewCTC,
    totalNewComponents,
    isNewSumMismatch,
    newSumDifference,
    totalComponentIncrease,
    actualPercentageIncrease,
    ctcPercentageIncrease,
    results,
  };
}
