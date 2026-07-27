from pydantic import BaseModel
from typing import Optional

class OnboardingTemplateCreate(BaseModel):
    pass

class OnboardingTemplateUpdate(BaseModel):
    pass

class OnboardingTemplateResponse(OnboardingTemplateCreate):
    id: str
