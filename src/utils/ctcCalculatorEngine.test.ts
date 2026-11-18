import {
  calculateCTCRevision,
  DEFAULT_EXAMPLE_COMPONENTS,
  DEFAULT_EMPLOYEE_DEDUCTIONS,
  formatIndianCurrency,
  formatPercentage,
} from './ctcCalculatorEngine.ts';
import type { CTCCalculatorState } from './ctcCalculatorEngine.ts';

function runTests() {
  console.log('--- Starting Proportional CTC Revision Calculator Engine Unit Tests ---');
  let passed = 0;
  let total = 0;

  function assert(condition: boolean, testName: string) {
    total++;
    if (condition) {
      console.log(`[PASS] ${testName}`);
      passed++;
    } else {
      console.error(`[FAIL] ${testName}`);
      throw new Error(`Test failed: ${testName}`);
    }
  }

  function approxEqual(a: number, b: number, eps = 0.001): boolean {
    return Math.abs(a - b) <= eps;
  }

  // Test Case 1: Core Business Example (Old CTC = 6,00,000, Target New CTC = 8,00,000)
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS,
      employeeDeductions: DEFAULT_EMPLOYEE_DEDUCTIONS,
    };

    const res = calculateCTCRevision(state);

    // 1. All old component percentages sum to 100% when old component total equals old CTC
    assert(approxEqual(res.oldEnteredCTC, 600000), 'Old CTC is 6,00,000');
    assert(approxEqual(res.totalOldComponents, 600000), 'Sum of old components is exactly 6,00,000');
    assert(approxEqual(res.oldComponentsPercentageSum, 100), 'Sum of old component percentages is 100%');
    assert(res.isOldSumMismatch === false, 'No old sum mismatch');

    // 2. Proportion derived for every component
    const basic = res.results.find((c) => c.id === 'basic')!;
    assert(approxEqual(basic.oldPercentageOfCTC, 40), 'Basic is exactly 40% of CTC');
    assert(approxEqual(basic.newAmount, 320000), 'Basic new amount is 40% of 8,00,000 = 3,20,000');
    assert(approxEqual(basic.monthlyEquivalent, 320000 / 12), 'Basic monthly equivalent is 320,000 / 12');

    const hra = res.results.find((c) => c.id === 'hra')!;
    assert(approxEqual(hra.oldPercentageOfCTC, 20), 'HRA is 20% of CTC');
    assert(approxEqual(hra.newAmount, 160000), 'HRA new amount is 20% of 8,00,000 = 1,60,000');

    const conv = res.results.find((c) => c.id === 'conveyance')!;
    assert(approxEqual(conv.oldPercentageOfCTC, 5), 'Conveyance is 5% of CTC');
    assert(approxEqual(conv.newAmount, 40000), 'Conveyance new amount is 5% of 8,00,000 = 40,000');

    const otherEarn = res.results.find((c) => c.id === 'other_earnings')!;
    assert(approxEqual(otherEarn.oldPercentageOfCTC, 20), 'Other Earnings is 20% of CTC');
    assert(approxEqual(otherEarn.newAmount, 160000), 'Other Earnings new amount is 1,60,000');

    // 3. Employer PF is PROPORTIONALLY recalculated (NO STATIC VALUE)
    const empPf = res.results.find((c) => c.id === 'employer_pf')!;
    assert(approxEqual(empPf.oldPercentageOfCTC, 4.8), 'Employer PF is 4.8% of CTC (28,800 / 600,000)');
    assert(approxEqual(empPf.newAmount, 38400), 'Employer PF is proportionally recalculated to 4.8% of 800,000 = 38,400');
    assert(empPf.newAmount !== empPf.oldAmount, 'Employer PF is NOT static (increased from 28,800 to 38,400)');

    // 4. Employer Pension is PROPORTIONALLY recalculated (NO STATIC VALUE)
    const empPension = res.results.find((c) => c.id === 'employer_pension')!;
    assert(approxEqual(empPension.oldPercentageOfCTC, 1.2), 'Employer Pension is 1.2% of CTC (7,200 / 600,000)');
    assert(approxEqual(empPension.newAmount, 9600), 'Employer Pension is proportionally recalculated to 1.2% of 800,000 = 9,600');
    assert(empPension.newAmount !== empPension.oldAmount, 'Employer Pension is NOT static (increased from 7,200 to 9,600)');

    // 5. LTA is PROPORTIONALLY recalculated and marked as annual benefit
    const lta = res.results.find((c) => c.id === 'lta')!;
    assert(approxEqual(lta.oldPercentageOfCTC, 4), 'LTA is 4% of CTC (24,000 / 600,000)');
    assert(approxEqual(lta.newAmount, 32000), 'LTA is proportionally recalculated to 4% of 800,000 = 32,000');
    assert(lta.isAnnualPayout === true, 'LTA is flagged as annual payout benefit');

    // 6. Gratuity is PROPORTIONALLY recalculated and marked as annual benefit
    const gratuity = res.results.find((c) => c.id === 'gratuity')!;
    assert(approxEqual(gratuity.oldPercentageOfCTC, 5), 'Gratuity is 5% of CTC (30,000 / 600,000)');
    assert(approxEqual(gratuity.newAmount, 40000), 'Gratuity is proportionally recalculated to 5% of 800,000 = 40,000');
    assert(gratuity.isAnnualPayout === true, 'Gratuity is flagged as annual benefit');

    // 7. New component amounts reconcile with the new CTC
    assert(approxEqual(res.totalNewComponents, 800000), 'Total New Components exactly matches target New CTC (8,00,000)');
    assert(res.isNewSumMismatch === false, 'No new sum mismatch when components reconcile');
    assert(approxEqual(res.newSumDifference, 0), 'New sum difference is 0');

    // 8. Employee PF deduction remains distinct from employer CTC
    const empDeduction = res.employeeDeductionResults?.find((d) => d.id === 'employee_pf')!;
    assert(empDeduction !== undefined, 'Employee deduction is tracked distinctly');
    assert(empDeduction.category === 'Employee Deduction', 'Category is Employee Deduction');
  }

  // Test Case 2: Percentage Increment Mode (Old CTC = 6,00,000 with 15% increment = 6,90,000)
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 15,
      targetCTC: 0,
      components: DEFAULT_EXAMPLE_COMPONENTS,
    };

    const res = calculateCTCRevision(state);
    assert(approxEqual(res.calculatedNewCTC, 690000), 'Percentage mode: 600,000 * 1.15 = 690,000');
    assert(approxEqual(res.totalNewComponents, 690000), 'Total new components equals 690,000');

    const empPf = res.results.find((c) => c.id === 'employer_pf')!;
    assert(approxEqual(empPf.newAmount, 28800 * 1.15), 'Employer PF increased by exactly 15%');

    const lta = res.results.find((c) => c.id === 'lta')!;
    assert(approxEqual(lta.newAmount, 24000 * 1.15), 'LTA increased by exactly 15%');

    const grat = res.results.find((c) => c.id === 'gratuity')!;
    assert(approxEqual(grat.newAmount, 30000 * 1.15), 'Gratuity increased by exactly 15%');
  }

  // Test Case 3: Old Component Total Mismatch produces warning and doesn't silently normalize
  {
    const stateMismatch: CTCCalculatorState = {
      oldCTC: 500000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 600000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', oldAmount: 200000 },
        { id: 'hra', name: 'HRA', category: 'Earning', oldAmount: 100000 },
      ], // Sum = 300,000 != 500,000
    };

    const res = calculateCTCRevision(stateMismatch);
    assert(res.isOldSumMismatch === true, 'Old sum mismatch is flagged');
    assert(approxEqual(res.oldSumDifference, -200000), 'Old sum difference is -200,000');
    // Basic was 200,000 / 500,000 = 40% of entered CTC
    const basic = res.results.find((c) => c.id === 'basic')!;
    assert(approxEqual(basic.oldPercentageOfCTC, 40), 'Basic percentage is calculated against entered Old CTC (40%), not normalized');
    assert(approxEqual(basic.newAmount, 240000), 'Basic new amount is 40% of 600,000 = 240,000');
  }

  // Test Case 4: Zero-value component handling & safe division by zero
  {
    const stateZero: CTCCalculatorState = {
      oldCTC: 0,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 10,
      targetCTC: 500000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', oldAmount: 0 },
        { id: 'conv', name: 'Conveyance', category: 'Earning', oldAmount: 0 },
      ],
    };

    const res = calculateCTCRevision(stateZero);
    assert(res.calculatedNewCTC === 0, 'Zero Old CTC in percentage mode produces 0');
    const basic = res.results.find((c) => c.id === 'basic')!;
    assert(basic.oldPercentageOfCTC === 0, 'Safe division by zero: percentage is 0');
    assert(basic.newAmount === 0, 'New amount is 0');
  }

  // Test Case 5: Currency and percentage formatting
  {
    assert(formatIndianCurrency(240000) === '₹2,40,000.00', 'Indian currency formatting works');
    assert(formatPercentage(40) === '40.00%', 'Percentage formatting works');
  }

  console.log(`\nALL ${passed}/${total} PROPORTIONAL ENGINE TESTS PASSED SUCCESSFULLY!`);
}

runTests();
