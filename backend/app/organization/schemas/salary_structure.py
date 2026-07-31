from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Any

class SalaryComponentSummary(BaseModel):
    id: str
    name: str
    componentType: Optional[str] = None
    calculationMethod: Optional[str] = None

class SalaryStructureCreate(BaseModel):
    name: str
    description: Optional[str] = None
    componentIds: List[str] = []   # list of SalaryComponent ObjectId strings

class SalaryStructureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    componentIds: Optional[List[str]] = None

class SalaryStructureResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    name: str
    description: Optional[str] = None
    componentIds: Optional[List[str]] = None
    components: Optional[List[SalaryComponentSummary]] = None   # enriched summaries
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
