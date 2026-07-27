from pydantic import BaseModel
from typing import Optional

class AttendanceSettingCreate(BaseModel):
    pass

class AttendanceSettingUpdate(BaseModel):
    pass

class AttendanceSettingResponse(AttendanceSettingCreate):
    id: str
