from typing import Optional
from app.core.models.base_model import BaseDBModel

class PayrollCycleModel(BaseDBModel):
    name: str
    startDate: str
    endDate: str
    processingStatus: str = "DRAFT"
    companyId: Optional[str] = None
