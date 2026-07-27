from pydantic import BaseModel
from typing import Optional

class EsiSettingCreate(BaseModel):
    pass

class EsiSettingUpdate(BaseModel):
    pass

class EsiSettingResponse(EsiSettingCreate):
    id: str
