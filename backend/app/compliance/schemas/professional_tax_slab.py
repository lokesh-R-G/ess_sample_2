from pydantic import BaseModel
from typing import Optional

class ProfessionalTaxSlabCreate(BaseModel):
    pass

class ProfessionalTaxSlabUpdate(BaseModel):
    pass

class ProfessionalTaxSlabResponse(ProfessionalTaxSlabCreate):
    id: str
