from pydantic import BaseModel
from typing import Optional

class PfContributionCreate(BaseModel):
    pass

class PfContributionUpdate(BaseModel):
    pass

class PfContributionResponse(PfContributionCreate):
    id: str
