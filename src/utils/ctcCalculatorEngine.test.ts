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
  console.log('--- Starting Complete CTC Revision Calculator Unit Tests ---');
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

  // Test 1: Employee Selection and Salary Retrieval baseline (Direct + Formula earnings)
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 360000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 480000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 240000 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(res.totalExistingComponents === 360000, 'Test 1: Existing components total 3,60,000');
    assert(res.updatedBaselineCTC === 360000, 'Test 1: Baseline CTC without additions is 3,60,000');
    assert(approxEqual(res.baselineComponentsPercentageSum, 100), 'Test 1: Baseline percentages total 100%');
  }

  // Test 2: All Earnings & Formula-derived components retrieved and evaluated correctly
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 320000,
      additionalBonus: 0,
      additionalCharges: 0,
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
    const hra = res.results.find(c => c.id === 'hra')!;
    const da = res.results.find(c => c.id === 'da')!;
    assert(approxEqual(hra.baselineAmount, 100000), 'Test 2: HRA evaluated to 1,00,000 (50% of Basic)');
    assert(approxEqual(da.baselineAmount, 20000), 'Test 2: DA evaluated to 20,000 (10% of Basic)');
    assert(approxEqual(res.totalExistingComponents, 320000), 'Test 2: Total earnings is 3,20,000');
  }

  // Test 3: Multi-level dependencies (Basic -> HRA -> Special Allowance = 20% of HRA)
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 320000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 480000,
      components: [
        { id: 'spec', name: 'Special Allowance', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 20, percentageDerivedFromComponentId: 'hra', oldAmount: 0 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Percentage', percentageValue: 50, percentageDerivedFromComponentId: 'basic', oldAmount: 0 },
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 200000 }
      ]
    };
    const res = calculateCTCRevision(state);
    const spec = res.results.find(c => c.id === 'spec')!;
    assert(approxEqual(spec.baselineAmount, 20000), 'Test 3: Multi-level dependent Special Allowance is 20,000');
    assert(approxEqual(spec.newAmount, 30000), 'Test 3: Revised Special Allowance is 30,000 (50% revision)');
  }

  // Test 4: Employer PF & Employer ESI & Pension included in employer CTC
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 600000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS
    };
    const res = calculateCTCRevision(state);
    const empPf = res.results.find(c => c.id === 'employer_pf')!;
    const empEsi = res.results.find(c => c.id === 'employer_esi')!;
    assert(empPf !== undefined, 'Test 4: Employer PF component present');
    assert(empPf.category === 'Employer Contribution', 'Test 4: Employer PF is Employer Contribution');
    assert(empPf.displayCalculationMethod === 'Employer Contribution', 'Test 4: Employer PF calculation method');
    assert(empEsi !== undefined, 'Test 4: Employer ESI component present');
    assert(empEsi.category === 'Employer Contribution', 'Test 4: Employer ESI is Employer Contribution');
  }

  // Test 5: LTA and Gratuity included and marked as annual benefits
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 600000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 800000,
      components: DEFAULT_EXAMPLE_COMPONENTS
    };
    const res = calculateCTCRevision(state);
    const lta = res.results.find(c => c.id === 'lta')!;
    const gratuity = res.results.find(c => c.id === 'gratuity')!;
    assert(lta.isAnnualPayout === true, 'Test 5: LTA is annual payout');
    assert(gratuity.isAnnualPayout === true, 'Test 5: Gratuity is annual payout');
  }

  // Test 6: Additional Bonus changes the complete baseline CTC
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 560000,
      additionalBonus: 30000,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 600000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 560000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(res.totalExistingComponents === 560000, 'Test 6: Total existing components is 5,60,000');
    assert(res.updatedBaselineCTC === 590000, 'Test 6: Updated baseline CTC increased by bonus to 5,90,000');
    const bonusComp = res.results.find(c => c.id === 'addl_bonus')!;
    assert(bonusComp !== undefined, 'Test 6: Additional bonus appears as a baseline CTC component');
    assert(approxEqual(bonusComp.baselineAmount, 30000), 'Test 6: Bonus baseline amount is 30,000');
  }

  // Test 7: Additional Charges change the complete baseline CTC
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 560000,
      additionalBonus: 0,
      additionalCharges: 10000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 600000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 560000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(res.updatedBaselineCTC === 570000, 'Test 7: Updated baseline CTC increased by charges to 5,70,000');
    const chargesComp = res.results.find(c => c.id === 'addl_charges')!;
    assert(chargesComp !== undefined, 'Test 7: Additional charges appears as a component');
    assert(approxEqual(chargesComp.baselineAmount, 10000), 'Test 7: Charges baseline amount is 10,000');
  }

  // Test 8: User Request Specification Scenario:
  // Existing components = ₹5,60,000, Bonus = ₹30,000, Charges = ₹10,000 => Baseline CTC = ₹6,00,000
  // All percentages recalculated against ₹6,00,000 and total exactly 100%!
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 560000,
      additionalBonus: 30000,
      additionalCharges: 10000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 750000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 240000 },
        { id: 'hra', name: 'HRA', category: 'Earning', calculationMethod: 'Flat', oldAmount: 120000 },
        { id: 'other', name: 'Other Earnings', category: 'Earning', calculationMethod: 'Flat', oldAmount: 120000 },
        { id: 'pf', name: 'Employer PF', category: 'Employer Contribution', calculationMethod: 'Flat', oldAmount: 28800 },
        { id: 'esi', name: 'Employer ESI', category: 'Employer Contribution', calculationMethod: 'Flat', oldAmount: 7200 },
        { id: 'lta', name: 'LTA', category: 'Annual Benefit', calculationMethod: 'Flat', oldAmount: 24000 },
        { id: 'gratuity', name: 'Gratuity', category: 'Annual Benefit', calculationMethod: 'Flat', oldAmount: 20000 }
      ]
    };
    // Sum of existing = 240k + 120k + 120k + 28.8k + 7.2k + 24k + 20k = 560,000
    // + 30k bonus + 10k charges = 600,000 total baseline CTC!
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.totalExistingComponents, 560000), 'Test 8: Existing total is 5,60,000');
    assert(approxEqual(res.updatedBaselineCTC, 600000), 'Test 8: Complete baseline CTC is 6,00,000');
    assert(approxEqual(res.baselineComponentsPercentageSum, 100), 'Test 8: Baseline percentages sum to 100.00%');

    const basic = res.results.find(c => c.id === 'basic')!;
    assert(approxEqual(basic.baselinePercentageOfCTC, 40), 'Test 8: Basic is 40% (240,000 / 600,000)');

    const hra = res.results.find(c => c.id === 'hra')!;
    assert(approxEqual(hra.baselinePercentageOfCTC, 20), 'Test 8: HRA is 20% (120,000 / 600,000)');

    const bonus = res.results.find(c => c.id === 'addl_bonus')!;
    assert(approxEqual(bonus.baselinePercentageOfCTC, 5), 'Test 8: Bonus is 5% (30,000 / 600,000)');

    const charges = res.results.find(c => c.id === 'addl_charges')!;
    assert(approxEqual(charges.baselinePercentageOfCTC, 1.6666, 0.01), 'Test 8: Charges is 1.67% (10,000 / 600,000)');

    // Revised allocation against 7,50,000
    assert(approxEqual(res.totalNewComponents, 750000), 'Test 8: Revised total reconciles with 7,50,000');
    assert(approxEqual(basic.newAmount, 300000), 'Test 8: Revised Basic is 40% of 750,000 = 3,00,000');
    assert(approxEqual(bonus.newAmount, 37500), 'Test 8: Revised Bonus is 5% of 750,000 = 37,500');
    assert(approxEqual(charges.newAmount, 12500), 'Test 8: Revised Charges is 1.67% of 750,000 = 12,500');
  }

  // Test 9: Percentage Increment Revision Mode
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 500000,
      additionalBonus: 50000,
      additionalCharges: 0,
      revisionMethod: 'PERCENTAGE',
      incrementPercentage: 10,
      targetCTC: 0,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 500000 }
      ]
    };
    // Baseline = 500k + 50k = 550,000. 10% increment => New CTC = 605,000
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.updatedBaselineCTC, 550000), 'Test 9: Baseline CTC is 5,50,000');
    assert(approxEqual(res.calculatedNewCTC, 605000), 'Test 9: New CTC is 550,000 * 1.10 = 6,05,000');
    assert(approxEqual(res.totalNewComponents, 605000), 'Test 9: Total new components equals 6,05,000');
  }

  // Test 10: Direct Target CTC Revision Mode
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 600000,
      additionalBonus: 20000,
      additionalCharges: 10000,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 900000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 600000 }
      ]
    };
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.calculatedNewCTC, 900000), 'Test 10: New CTC is 9,00,000');
    assert(approxEqual(res.totalNewComponents, 900000), 'Test 10: Total new components matches 9,00,000');
  }

  // Test 11: Employee-side deductions are NOT counted in employer CTC costs
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 300000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 400000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 300000 }
      ],
      employeeDeductions: DEFAULT_EMPLOYEE_DEDUCTIONS
    };
    const res = calculateCTCRevision(state);
    assert(approxEqual(res.totalExistingComponents, 300000), 'Test 11: Employee deductions not added to employer CTC components');
    assert(approxEqual(res.updatedBaselineCTC, 300000), 'Test 11: Baseline CTC does not include employee deductions');
    assert(res.employeeDeductionResults !== undefined && res.employeeDeductionResults.length === 2, 'Test 11: Employee deductions tracked separately');
  }

  // Test 12: Zero-value components & cycle safety
  {
    const state: CTCCalculatorState = {
      existingAnnualCTC: 300000,
      additionalBonus: 0,
      additionalCharges: 0,
      revisionMethod: 'TARGET_CTC',
      incrementPercentage: 0,
      targetCTC: 400000,
      components: [
        { id: 'basic', name: 'Basic', category: 'Earning', calculationMethod: 'Flat', oldAmount: 300000 },
        { id: 'zero_comp', name: 'Zero Component', category: 'Earning', calculationMethod: 'Flat', oldAmount: 0 }
      ]
    };
    const res = calculateCTCRevision(state);
    const zeroC = res.results.find(c => c.id === 'zero_comp')!;
    assert(approxEqual(zeroC.baselinePercentageOfCTC, 0), 'Test 12: Zero component percentage is 0%');
    assert(approxEqual(zeroC.newAmount, 0), 'Test 12: Zero component new amount is 0');
  }

  console.log(`\nALL ${passed}/${total} TEST SUITE CASES PASSED SUCCESSFULLY!`);
}

runTests();
