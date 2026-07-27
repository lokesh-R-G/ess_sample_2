from pydantic import BaseModel
from typing import Optional

class TdsSettingCreate(BaseModel):
    pass

class TdsSettingUpdate(BaseModel):
    pass

class TdsSettingResponse(TdsSettingCreate):
    id: str
