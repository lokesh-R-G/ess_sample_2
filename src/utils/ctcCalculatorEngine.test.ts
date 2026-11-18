import {
  calculateCTCRevision,
  DEFAULT_EXCEL_COMPONENTS,
  formatIndianCurrency,
} from './ctcCalculatorEngine.ts';
import type { CTCCalculatorState } from './ctcCalculatorEngine.ts';

function runTests() {
  console.log('--- Starting CTC Revision Calculator Engine Unit Tests ---');
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

  function approxEqual(a: number, b: number, eps = 0.0001): boolean {
    return Math.abs(a - b) <= eps;
  }

  // Test 1: Excel Baseline Reference Test
  {
    const state: CTCCalculatorState = {
      oldCTC: 1400004,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 2400000,
      components: DEFAULT_EXCEL_COMPONENTS,
    };

    const res = calculateCTCRevision(state);

    assert(approxEqual(res.oldEnteredCTC, 1400004), 'Excel Old CTC is 1,400,004');
    assert(approxEqual(res.totalOldComponents, 1450404), 'Excel Total Old Components is 1,450,404');
    assert(res.isOldSumMismatch === true, 'Excel Old Sum Mismatch detected (1,450,404 != 1,400,004)');
    assert(approxEqual(res.oldSumDifference, 50400), 'Old Sum difference is exactly 50,400');

    assert(approxEqual(res.calculatedNewCTC, 2400000), 'Calculated New CTC is 2,400,000');
    assert(approxEqual(res.totalNewComponents, 2433685.8288976), 'Total New Components matches Excel ~2433685.83');
    assert(res.isNewSumMismatch === true, 'New Sum Mismatch detected due to fixed PF');
    assert(approxEqual(res.newSumDifference, 33685.8288976), 'New Sum difference is ~33685.83');

    // Check specific components
    const basic = res.results.find((c) => c.name === 'Basic')!;
    assert(approxEqual(basic.oldPercentageOfCTC, 630000 / 1400004), 'Basic % of Old CTC is ~0.4499987');
    assert(approxEqual(basic.newAmount, 1079996.91429), 'Basic New Amount is 1,079,996.91');

    const hra = res.results.find((c) => c.name === 'HRA')!;
    assert(approxEqual(hra.newAmount, 539998.45714), 'HRA New Amount is 539,998.46');

    // Static PF checks
    const pfEmp = res.results.find((c) => c.name === 'PF Employee (PFEMP)')!;
    assert(pfEmp.isStatic === true, 'PF Employee is marked static');
    assert(approxEqual(pfEmp.newAmount, 36000), 'PF Employee newAmount is fixed at 36,000');
    assert(approxEqual(pfEmp.difference, 0), 'PF Employee difference is 0');

    const pfEmpr = res.results.find((c) => c.name === 'PF Employer (EPEMPR)')!;
    assert(approxEqual(pfEmpr.newAmount, 37800), 'PF Employer newAmount is fixed at 37,800');

    const epsEmpr = res.results.find((c) => c.name === 'EPS Employer (EPSEMPR)')!;
    assert(approxEqual(epsEmpr.newAmount, 0), 'EPS Employer newAmount is fixed at 0');
  }

  // Test 2: Mode A Percentage Increment Calculation
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 15,
      targetCTC: 0,
      components: [
        { id: 'basic', name: 'Basic', oldAmount: 300000, isStatic: false },
        { id: 'pf_emp', name: 'PF Employee (PFEMP)', oldAmount: 21600, isStatic: true },
      ],
    };

    const res = calculateCTCRevision(state);
    assert(approxEqual(res.calculatedNewCTC, 690000), 'Percentage mode: 600,000 * 1.15 = 690,000');

    const basic = res.results.find((c) => c.id === 'basic')!;
    assert(approxEqual(basic.oldPercentageOfCTC, 0.5), 'Basic percentage is 50%');
    assert(approxEqual(basic.newAmount, 345000), 'Basic new amount is 345,000');

    const pfEmp = res.results.find((c) => c.id === 'pf_emp')!;
    assert(approxEqual(pfEmp.newAmount, 21600), 'Static PF remains 21,600');
  }

  // Test 3: Zero-value components and zero Old CTC safety
  {
    const stateZeroCTC: CTCCalculatorState = {
      oldCTC: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 10,
      targetCTC: 500000,
      components: [
        { id: 'basic', name: 'Basic', oldAmount: 0, isStatic: false },
        { id: 'pf_emp', name: 'PF Employee (PFEMP)', oldAmount: 10000, isStatic: true },
      ],
    };

    const res = calculateCTCRevision(stateZeroCTC);
    assert(res.calculatedNewCTC === 500000, 'Calculated CTC handled');
    const basic = res.results.find((c) => c.id === 'basic')!;
    assert(basic.oldPercentageOfCTC === 0, 'No division by zero: pct is 0');
    assert(basic.newAmount === 0, 'New amount is 0');
    const pf = res.results.find((c) => c.id === 'pf_emp')!;
    assert(pf.newAmount === 10000, 'Static PF remains unchanged even with 0 old CTC');
  }

  // Test 4: Switching between revision methods
  {
    const baseState: CTCCalculatorState = {
      oldCTC: 1000000,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 20,
      targetCTC: 1500000,
      components: [{ id: 'basic', name: 'Basic', oldAmount: 500000, isStatic: false }],
    };

    const resPct = calculateCTCRevision(baseState);
    assert(approxEqual(resPct.calculatedNewCTC, 1200000), 'Method PERCENTAGE yields 1,200,000');

    const resTarget = calculateCTCRevision({ ...baseState, revisionMethod: 'TARGET_CTC' });
    assert(approxEqual(resTarget.calculatedNewCTC, 1500000), 'Method TARGET_CTC yields 1,500,000');
  }

  // Test 5: Editing an old component updates result immediately
  {
    const state1: CTCCalculatorState = {
      oldCTC: 1000000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 1200000,
      components: [{ id: 'basic', name: 'Basic', oldAmount: 500000, isStatic: false }],
    };
    const res1 = calculateCTCRevision(state1);
    assert(approxEqual(res1.results[0].newAmount, 600000), 'Initial basic new is 600,000');

    const state2: CTCCalculatorState = {
      ...state1,
      components: [{ id: 'basic', name: 'Basic', oldAmount: 600000, isStatic: false }],
    };
    const res2 = calculateCTCRevision(state2);
    assert(approxEqual(res2.results[0].newAmount, 720000), 'Updated basic old 600k yields new 720k');
  }

  // Test 6: Currency formatting
  {
    assert(formatIndianCurrency(1079996.91) === '₹10,79,996.91', 'Indian currency formatting works');
    assert(formatIndianCurrency(0) === '₹0.00', 'Indian currency zero formatting works');
  }

  console.log(`\nALL ${passed}/${total} TESTS PASSED SUCCESSFULLY!`);
}

runTests();
