from pydantic import BaseModel
from typing import Optional

class PtSettingCreate(BaseModel):
    pass

class PtSettingUpdate(BaseModel):
    pass

class PtSettingResponse(PtSettingCreate):
    id: str
