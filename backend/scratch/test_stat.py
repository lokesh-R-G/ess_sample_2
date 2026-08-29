import asyncio
from app.payroll.services.salary_calculation_engine import StatutoryDecisions

def test():
    # 1. Test None
    dec1 = StatutoryDecisions(
        isFresher=None,
        isExistingPensionMember=None,
        wantsPf=None,
        wantsPension=None,
        pfCalculationMode=None,
        esiEnabled=None,
        ptState=None
    )
    print("Test 1 (None):", dec1)
    
    # 2. Test valid values
    dec2 = StatutoryDecisions(
        isFresher=False,
        isExistingPensionMember=True,
        wantsPf=False,
        wantsPension=False,
        pfCalculationMode="Actual",
        esiEnabled=False,
        ptState="Karnataka"
    )
    print("Test 2 (Values):", dec2)

if __name__ == "__main__":
    test()
