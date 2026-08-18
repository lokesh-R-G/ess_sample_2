from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AttachmentModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    claimId: str
    fileName: str
    mimeType: str
    storagePath: str
    
    # Audit
    createdAt: Optional[datetime] = None
    uploadedBy: Optional[str] = None
