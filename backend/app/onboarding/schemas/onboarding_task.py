from pydantic import BaseModel
from typing import Optional

class OnboardingTaskCreate(BaseModel):
    pass

class OnboardingTaskUpdate(BaseModel):
    pass

class OnboardingTaskResponse(OnboardingTaskCreate):
    id: str
