from pydantic import BaseModel
from typing import Optional

class EsiContributionCreate(BaseModel):
    pass

class EsiContributionUpdate(BaseModel):
    pass

class EsiContributionResponse(EsiContributionCreate):
    id: str
