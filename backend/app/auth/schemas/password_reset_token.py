from pydantic import BaseModel
from typing import Optional

class PasswordResetTokenCreate(BaseModel):
    pass

class PasswordResetTokenUpdate(BaseModel):
    pass

class PasswordResetTokenResponse(PasswordResetTokenCreate):
    id: str
