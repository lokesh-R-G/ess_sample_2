from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal

class SalaryComponentCreate(BaseModel):
    name: str
    code: Optional[str] = None
    componentType: Literal["Earning", "Deduction"]
    calculationMethod: Literal["Flat", "Percentage", "Formula"] = "Flat"
    # Percentage-specific fields — only relevant when calculationMethod == "Percentage"
    percentageValue: Optional[float] = None
    percentageDerivedFrom: Optional[str] = None   # e.g. "Gross Salary", "Basic Pay"
    defaultFormula: Optional[str] = None
    isTaxable: bool = True
    pfApplicable: bool = False
    esiApplicable: bool = False
    displayOrder: int = 1
    isActive: bool = True

class SalaryComponentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    componentType: Optional[Literal["Earning", "Deduction"]] = None
    calculationMethod: Optional[Literal["Flat", "Percentage", "Formula"]] = None
    percentageValue: Optional[float] = None
    percentageDerivedFrom: Optional[str] = None
    defaultFormula: Optional[str] = None
    isTaxable: Optional[bool] = None
    pfApplicable: Optional[bool] = None
    esiApplicable: Optional[bool] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None

class SalaryComponentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    name: str
    code: Optional[str] = None
    componentType: Optional[str] = None
    calculationMethod: Optional[str] = None
    percentageValue: Optional[float] = None
    percentageDerivedFrom: Optional[str] = None
    defaultFormula: Optional[str] = None
    isTaxable: Optional[bool] = None
    pfApplicable: Optional[bool] = None
    esiApplicable: Optional[bool] = None
    # Legacy field aliases for backward compat
    pfApplicability: Optional[bool] = None
    esiApplicability: Optional[bool] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
