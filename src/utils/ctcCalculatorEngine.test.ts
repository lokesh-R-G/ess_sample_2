import {
  calculateCTCRevision,
  DEFAULT_EXAMPLE_COMPONENTS,
  DEFAULT_EMPLOYEE_DEDUCTIONS,
  formatIndianCurrency,
  formatPercentage,
  resolveComponentDependencies
} from './ctcCalculatorEngine.ts';
import type { CTCCalculatorState, CTCComponentInput } from './ctcCalculatorEngine.ts';

function runTests() {
  console.log('--- Starting Proportional & Formula-Derived CTC Calculator Unit Tests ---');
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

  // Test 1: Direct earning component
  {
    const state: CTCCalculatorState = {
      oldCTC: 300000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 450000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 300000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(res.results.length === 1, 'Test 1: Single direct component created');
    assert(res.results[0].displayCalculationMethod === 'Direct Input', 'Test 1: Calculation method is Direct Input');
    assert(approxEqual(res.results[0].oldAmount, 300000), 'Test 1: Old amount is 3,00,000');
    assert(approxEqual(res.results[0].newAmount, 450000), 'Test 1: New amount is 4,50,000');
    assert(approxEqual(res.totalNewComponents, 450000), 'Test 1: Total matches new target CTC');
  }

  // Test 2: One formula-derived earning component (HRA = 50% of Basic)
  {
    const state: CTCCalculatorState = {
      oldCTC: 360000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 480000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 240000 },
        {
          id: 'hra',
          name: 'HRA',
          category: 'Earning',
          calculationMethod: 'Percentage',
          percentageValue: 50,
          percentageDerivedFromComponentId: 'basic',
          oldAmount: 0 // derived from basic
        }
      ]
    };
    const res = calculateCTCRevision(state);
    const hra = res.results.find(c => c.id === 'hra')!;
    const basic = res.results.find(c => c.id === 'basic')!;

    assert(hra.displayCalculationMethod === 'Formula Derived', 'Test 2: HRA is Formula Derived');
    assert(hra.isFormulaDerived === true, 'Test 2: HRA is flagged as formula-derived');
    assert(approxEqual(hra.oldAmount, 120000), 'Test 2: HRA old amount derived as 50% of 2,40,000 = 1,20,000');
    assert(approxEqual(res.totalOldComponents, 360000), 'Test 2: Total old components is 3,60,000');
    assert(approxEqual(basic.newAmount, 320000), 'Test 2: Revised Basic is 3,20,000');
    assert(approxEqual(hra.newAmount, 160000), 'Test 2: Revised HRA is 50% of revised Basic = 1,60,000');
    assert(approxEqual(res.totalNewComponents, 480000), 'Test 2: Total new components matches target 4,80,000');
  }

  // Test 3: Multiple formula-derived components (HRA = 50% of Basic, DA = 10% of Basic)
  {
    const state: CTCCalculatorState = {
      oldCTC: 320000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 400000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 200000 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 },
        { id: 'da', name: 'DA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 10, percentageDerivedFromComponentId: 'basic', oldAmount: 0 }
      ]
    };
    const res = calculateCTCRevision(state);
    const basic = res.results.find(c => c.id === 'basic')!;
    const hra = res.results.find(c => c.id === 'hra')!;
    const da = res.results.find(c => c.id === 'da')!;

    assert(approxEqual(hra.oldAmount, 100000), 'Test 3: HRA old is 1,00,000 (50%)');
    assert(approxEqual(da.oldAmount, 20000), 'Test 3: DA old is 20,000 (10%)');
    assert(approxEqual(res.totalOldComponents, 320000), 'Test 3: Total old is 3,20,000');
    assert(approxEqual(basic.newAmount, 250000), 'Test 3: Basic new is 2,50,000');
    assert(approxEqual(hra.newAmount, 125000), 'Test 3: HRA new is 1,25,000 (50% of 250,000)');
    assert(approxEqual(da.newAmount, 25000), 'Test 3: DA new is 25,000 (10% of 250,000)');
    assert(approxEqual(res.totalNewComponents, 400000), 'Test 3: Total new components reconciles to 4,00,000');
  }

  // Test 4: Multi-level dependencies (Basic -> HRA -> Special Allowance = 20% of HRA)
  {
    const state: CTCCalculatorState = {
      oldCTC: 320000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 480000, // 50% increase: 320,000 * 1.5 = 480,000
      components: [
        // Dependent listed BEFORE parent to test topological ordering
        { id: 'spec', name: 'Special Allowance', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 20, percentageDerivedFromComponentId: 'hra', oldAmount: 0 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 },
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 200000 }
      ]
    };
    const res = calculateCTCRevision(state);
    const basic = res.results.find(c => c.id === 'basic')!;
    const hra = res.results.find(c => c.id === 'hra')!;
    const spec = res.results.find(c => c.id === 'spec')!;

    assert(approxEqual(hra.oldAmount, 100000), 'Test 4: HRA old evaluated to 1,00,000');
    assert(approxEqual(spec.oldAmount, 20000), 'Test 4: Special allowance old evaluated to 20,000 (20% of HRA)');
    assert(approxEqual(res.totalOldComponents, 320000), 'Test 4: Total old components is 3,20,000');
    assert(approxEqual(basic.newAmount, 300000), 'Test 4: Basic new is 3,00,000');
    assert(approxEqual(hra.newAmount, 150000), 'Test 4: HRA new is 1,50,000');
    assert(approxEqual(spec.newAmount, 30000), 'Test 4: Special allowance new is 30,000 (20% of 150,000)');
    assert(approxEqual(res.totalNewComponents, 480000), 'Test 4: Total new components matches 4,80,000');
  }

  // Test 5: Employer PF and pension components
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS
    };
    const res = calculateCTCRevision(state);
    const empPf = res.results.find(c => c.id === 'employer_pf')!;
    const empPension = res.results.find(c => c.id === 'employer_pension')!;

    assert(empPf.category === 'Employer Contribution', 'Test 5: Employer PF category');
    assert(empPf.displayCalculationMethod === 'Employer Contribution', 'Test 5: Employer PF display method');
    assert(approxEqual(empPf.newAmount, 38400), 'Test 5: Employer PF revised to 38,400');
    assert(empPension.category === 'Employer Contribution', 'Test 5: Employer Pension category');
    assert(approxEqual(empPension.newAmount, 9600), 'Test 5: Employer Pension revised to 9,600');
  }

  // Test 6: LTA and gratuity
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS
    };
    const res = calculateCTCRevision(state);
    const lta = res.results.find(c => c.id === 'lta')!;
    const gratuity = res.results.find(c => c.id === 'gratuity')!;

    assert(lta.category === 'Annual Benefit', 'Test 6: LTA category is Annual Benefit');
    assert(lta.displayCalculationMethod === 'Annual Benefit', 'Test 6: LTA display method is Annual Benefit');
    assert(lta.isAnnualPayout === true, 'Test 6: LTA is flagged as annual payout');
    assert(approxEqual(lta.newAmount, 32000), 'Test 6: LTA revised to 32,000');
    assert(gratuity.isAnnualPayout === true, 'Test 6: Gratuity is flagged as annual payout');
    assert(approxEqual(gratuity.newAmount, 40000), 'Test 6: Gratuity revised to 40,000');
  }

  // Test 7: Zero-value components
  {
    const state: CTCCalculatorState = {
      oldCTC: 300000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 400000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 300000 },
        { id: 'bonus', name: 'Zero Bonus', category: 'Earning', calculationMethod: 'Flat', oldAmount: 0 },
        { id: 'zero_derived', name: 'Zero Derived', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 0, percentageDerivedFromComponentId: 'basic', oldAmount: 0 }
      ]
    };
    const res = calculateCTCRevision(state);
    const zeroDerived = res.results.find(c => c.id === 'zero_derived')!;
    const bonus = res.results.find(c => c.id === 'bonus')!;

    assert(approxEqual(bonus.newAmount, 0), 'Test 7: Zero flat component remains 0');
    assert(approxEqual(zeroDerived.newAmount, 0), 'Test 7: Zero derived component remains 0');
    assert(approxEqual(res.totalNewComponents, 400000), 'Test 7: Total reconciles cleanly');
  }

  // Test 8: Circular formula dependency (A -> B -> A)
  {
    const comps: CTCComponentInput[] = [
      { id: 'a', name: 'Comp A', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'b', oldAmount: 0 },
      { id: 'b', name: 'Comp B', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'a', oldAmount: 0 }
    ];
    const depRes = resolveComponentDependencies(comps);
    assert(depRes.circularError !== undefined, 'Test 8: Circular dependency detected in Kahn graph');
    assert(depRes.circularError!.includes('Circular dependency'), 'Test 8: Error message specifies circularity');

    const state: CTCCalculatorState = {
      oldCTC: 100000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 120000,
      components: comps
    };
    const res = calculateCTCRevision(state);
    assert(res.calculationWarnings !== undefined && res.calculationWarnings.length > 0, 'Test 8: Calculator emits circular warning');
  }

  // Test 9: Missing formula dependency (Component references non-existent parent)
  {
    const comps: CTCComponentInput[] = [
      { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 100000 },
      { id: 'orphan', name: 'Orphan', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 20, percentageDerivedFromComponentId: 'non_existent_id', oldAmount: 5000 }
    ];
    const depRes = resolveComponentDependencies(comps);
    assert(depRes.missingDependencies['orphan'] === 'non_existent_id', 'Test 9: Missing dependency detected');

    const state: CTCCalculatorState = {
      oldCTC: 105000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 210000,
      components: comps
    };
    const res = calculateCTCRevision(state);
    const orphan = res.results.find(c => c.id === 'orphan')!;
    assert(orphan.evaluationError !== undefined, 'Test 9: Orphan component has evaluation error');
    assert(orphan.newAmount > 0, 'Test 9: Graceful fallback ensures no crash');
  }

  // Test 10: Complete CTC reconciliation (All components sum exactly to CTC)
  {
    const state: CTCCalculatorState = {
      oldCTC: 600000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS
    };
    const res = calculateCTCRevision(state);
    assert(res.isOldSumMismatch === false, 'Test 10: Old sum perfectly reconciles');
    assert(res.isNewSumMismatch === false, 'Test 10: New sum perfectly reconciles');
    assert(approxEqual(res.oldComponentsPercentageSum, 100.0), 'Test 10: Old component percentages sum to 100%');
    assert(approxEqual(res.totalNewComponents, 800000), 'Test 10: Total new components matches target 8,00,000');
  }

  // Test 11: Percentage increment revision (e.g. 20% increment)
  {
    const state: CTCCalculatorState = {
      oldCTC: 500000,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 20,
      targetCTC: 0,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 250000 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 },
        { id: 'other', name: 'Other', category: 'Earning', calculationMethod: 'Flat', oldAmount: 125000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.calculatedNewCTC, 600000), 'Test 11: New CTC is 5,00,000 * 1.20 = 6,00,000');
    assert(approxEqual(res.totalNewComponents, 600000), 'Test 11: Total new components equals 6,00,000');
    const basic = res.results.find(c => c.id === 'basic')!;
    const hra = res.results.find(c => c.id === 'hra')!;
    assert(approxEqual(basic.newAmount, 300000), 'Test 11: Basic grew by 20% to 3,00,000');
    assert(approxEqual(hra.newAmount, 150000), 'Test 11: HRA grew by 20% to 1,50,000');
  }

  // Test 12: Direct target CTC revision
  {
    const state: CTCCalculatorState = {
      oldCTC: 500000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 750000, // 50% increase
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 250000 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 },
        { id: 'other', name: 'Other', category: 'Earning', calculationMethod: 'Flat', oldAmount: 125000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.calculatedNewCTC, 750000), 'Test 12: Target CTC is 7,50,000');
    assert(approxEqual(res.totalNewComponents, 750000), 'Test 12: Total new components equals 7,50,000');
    assert(approxEqual(res.incrementPercentage, 50), 'Test 12: Increment percentage calculated as 50%');
  }

  console.log(`\nALL ${passed}/${total} TEST SUITE CASES PASSED SUCCESSFULLY!`);
}

runTests();
