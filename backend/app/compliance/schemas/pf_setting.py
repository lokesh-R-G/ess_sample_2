from pydantic import BaseModel
from typing import Optional

class PfSettingCreate(BaseModel):
    pass

class PfSettingUpdate(BaseModel):
    pass

class PfSettingResponse(PfSettingCreate):
    id: str
