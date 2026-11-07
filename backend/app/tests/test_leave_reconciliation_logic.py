"""
Test Suite for Historical Leave Reconciliation Logic
===================================================
Tests confirmed Excel-to-ESS leave balance calculation mapping:
- ELIG -> credited
- AVAILED -> consumed
- availableBalance = (credited + carriedForward) - consumed
- ELIG - AVAILED == availableBalance (when carriedForward == 0)
- Negative balance handling (no clamping)
- Fractional leave values
- Invariant preservation
"""

import unittest

def calculate_ledger_balances(
    excel_elig: float,
    excel_availed: float,
    exist_op_bal: float = 12.0,
    exist_cf: float = 0.0,
    workbook_op_bal: float = None
):
    """Encapsulation of the reconciliation calculation formula."""
    proposed_credited = float(excel_elig)
    proposed_consumed = float(excel_availed)
    proposed_cf = float(exist_cf)
    
    if workbook_op_bal is not None:
        proposed_op_bal = float(workbook_op_bal)
    else:
        proposed_op_bal = proposed_credited

    proposed_avail = (proposed_credited + proposed_cf) - proposed_consumed
    return {
        "credited": proposed_credited,
        "consumed": proposed_consumed,
        "carriedForward": proposed_cf,
        "openingBalance": proposed_op_bal,
        "availableBalance": proposed_avail
    }

class TestLeaveReconciliationLogic(unittest.TestCase):

    def test_standard_example(self):
        """ELIG = 12, AVAILED = 4 -> Credited = 12, Consumed = 4, Available = 8"""
        res = calculate_ledger_balances(excel_elig=12, excel_availed=4)
        self.assertEqual(res["credited"], 12.0)
        self.assertEqual(res["consumed"], 4.0)
        self.assertEqual(res["availableBalance"], 8.0)
        self.assertEqual(res["openingBalance"], 12.0)

    def test_zero_availed(self):
        """ELIG = 12, AVAILED = 0 -> Available = 12"""
        res = calculate_ledger_balances(excel_elig=12, excel_availed=0)
        self.assertEqual(res["credited"], 12.0)
        self.assertEqual(res["consumed"], 0.0)
        self.assertEqual(res["availableBalance"], 12.0)

    def test_full_availed(self):
        """ELIG = 12, AVAILED = 12 -> Available = 0"""
        res = calculate_ledger_balances(excel_elig=12, excel_availed=12)
        self.assertEqual(res["credited"], 12.0)
        self.assertEqual(res["consumed"], 12.0)
        self.assertEqual(res["availableBalance"], 0.0)

    def test_negative_balance_no_clamping(self):
        """ELIG = 6, AVAILED = 8 -> Available = -2 (must not be clamped to 0)"""
        res = calculate_ledger_balances(excel_elig=6, excel_availed=8)
        self.assertEqual(res["credited"], 6.0)
        self.assertEqual(res["consumed"], 8.0)
        self.assertEqual(res["availableBalance"], -2.0)

    def test_fractional_values(self):
        """ELIG = 12.5, AVAILED = 11.5 -> Available = 1.0"""
        res = calculate_ledger_balances(excel_elig=12.5, excel_availed=11.5)
        self.assertEqual(res["credited"], 12.5)
        self.assertEqual(res["consumed"], 11.5)
        self.assertEqual(res["availableBalance"], 1.0)

    def test_carried_forward_invariant(self):
        """ELIG = 10, AVAILED = 4, CF = 3 -> Available = (10 + 3) - 4 = 9"""
        res = calculate_ledger_balances(excel_elig=10, excel_availed=4, exist_cf=3.0)
        self.assertEqual(res["credited"], 10.0)
        self.assertEqual(res["carriedForward"], 3.0)
        self.assertEqual(res["consumed"], 4.0)
        self.assertEqual(res["availableBalance"], 9.0)

    def test_distinct_workbook_opening_balance(self):
        """Distinct opening balance from workbook col 23 (e.g. 36) mapped to openingBalance"""
        res = calculate_ledger_balances(excel_elig=12, excel_availed=9, workbook_op_bal=36.0)
        self.assertEqual(res["credited"], 12.0)
        self.assertEqual(res["consumed"], 9.0)
        self.assertEqual(res["availableBalance"], 3.0)
        self.assertEqual(res["openingBalance"], 36.0)

if __name__ == "__main__":
    unittest.main()

