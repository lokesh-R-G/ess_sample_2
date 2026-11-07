import os

file_path = "app/attendance_v2/routes/admin_attendance_routes.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

imports_to_add = """from pydantic import BaseModel, Field
from datetime import timezone
from fastapi import Body
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService

class ManualAttendanceRequest(BaseModel):
    status: str = Field(..., description="PRESENT, ABSENT, or LOP")
    lopHours: float = None

"""

if "ManualAttendanceRequest" not in content:
    with open(file_path, "w", encoding="utf-8") as f:
        # Prepend imports to the second line to keep typing at the top
        lines = content.split('\n')
        lines.insert(2, imports_to_add)
        f.write('\n'.join(lines))
