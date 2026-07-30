from pydantic import BaseModel
from typing import Optional, Literal

class SalaryComponentCreate(BaseModel):
    companyId: str
    name: str
    code: Optional[str] = None
    componentType: Literal["Earning", "Deduction"]
    calculationMethod: Literal["Flat", "Percentage", "Formula"] = "Flat"
    defaultFormula: Optional[str] = None
    isTaxable: bool = True
    pfApplicability: bool = False
    esiApplicability: bool = False
    displayOrder: int = 1
    isActive: bool = True

class SalaryComponentUpdate(BaseModel):
    companyId: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    componentType: Optional[Literal["Earning", "Deduction"]] = None
    calculationMethod: Optional[Literal["Flat", "Percentage", "Formula"]] = None
    defaultFormula: Optional[str] = None
    isTaxable: Optional[bool] = None
    pfApplicability: Optional[bool] = None
    esiApplicability: Optional[bool] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None

class SalaryComponentResponse(SalaryComponentCreate):
    id: str
