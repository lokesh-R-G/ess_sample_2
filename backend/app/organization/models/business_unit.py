from typing import Optional
from pydantic import Field, ConfigDict
from app.core.models.base_model import BaseDBModel

class BusinessUnitModel(BaseDBModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = Field(default=None, alias="_id")
