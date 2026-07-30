from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LocationModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
