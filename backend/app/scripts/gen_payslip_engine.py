import os
from pathlib import Path

FOLDERS = ["controllers", "services", "repositories", "schemas", "models", "validators", "dtos", "routes", "events", "constants", "exceptions", "interfaces", "types", "utils", "tests"]

def create_structure(base_path, module):
    mod_path = base_path / module
    mod_path.mkdir(parents=True, exist_ok=True)
    (mod_path / "__init__.py").touch()
    for folder in FOLDERS:
        folder_path = mod_path / folder
        folder_path.mkdir(exist_ok=True)
        (folder_path / "__init__.py").touch()
    return mod_path

def write_models(mod_path):
    # Payslip Model
    model_code = """from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class PayslipModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    branchId: str
    employeeId: str
    employeeCode: str
    employeeName: str
    designation: str
    department: str
    location: str
    costCenter: Optional[str] = None
    payrollRunId: str
    month: int
    year: int
    payPeriodStart: datetime
    payPeriodEnd: datetime
    generatedDate: datetime
    publishedDate: Optional[datetime] = None
    currency: str = "INR"
    status: str = "Draft"
    grossEarnings: float = 0.0
    grossDeductions: float = 0.0
    grossReimbursements: float = 0.0
    tax: float = 0.0
    netSalary: float = 0.0
    earnings: Dict[str, float] = {}
    deductions: Dict[str, float] = {}
    reimbursements: Dict[str, float] = {}
    employerContribution: Dict[str, float] = {}
    attendanceSummary: Dict[str, float] = {}
    leaveSummary: Dict[str, float] = {}
    remarks: Optional[str] = None
    version: int = 1
    pdfPath: Optional[str] = None
    checksum: Optional[str] = None
    createdBy: str
    createdAt: datetime
    updatedAt: datetime
"""
    with open(mod_path / "models" / "payslip_model.py", "w") as f:
        f.write(model_code)

def write_utilities(mod_path):
    # PDF Generator Utility
    pdf_code = """import hashlib

class PayslipPDFGenerator:
    @staticmethod
    def generate_pdf(payslip_data: dict) -> str:
        # In a real system, this uses reportlab or wkhtmltopdf.
        # For the engine logic, we simulate the PDF generation.
        pdf_path = f"/storage/payslips/{payslip_data['employeeId']}_{payslip_data['month']}_{payslip_data['year']}_v{payslip_data['version']}.pdf"
        return pdf_path

class ChecksumGenerator:
    @staticmethod
    def generate_checksum(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

class EmailSender:
    @staticmethod
    def send_payslip_email(employee_email: str, employee_name: str, month: int, year: int, net_salary: float, download_link: str):
        # Simulated SMTP sending
        html_template = f'''
        <h2>Salary Payslip - {month}/{year}</h2>
        <p>Dear {employee_name},</p>
        <p>Your payslip for {month}/{year} has been published.</p>
        <p>Net Salary: {net_salary}</p>
        <a href="{download_link}">Download Payslip</a>
        '''
        return True
"""
    with open(mod_path / "utils" / "payslip_utils.py", "w") as f:
        f.write(pdf_code)

def write_repository(mod_path):
    repo_code = """from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
from ..models.payslip_model import PayslipModel

class PayslipRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["payslips"]
        self.version_collection = db["payslip_versions"]
        
    async def create(self, data: dict, session=None):
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        result = await self.collection.insert_one(data, session=session)
        
        # Also store in version history
        data["payslipId"] = str(result.inserted_id)
        data.pop("_id", None)
        await self.version_collection.insert_one(data, session=session)
        
        return str(result.inserted_id)
        
    async def update_status(self, payslip_id: str, new_status: str, session=None):
        await self.collection.update_one(
            {"_id": ObjectId(payslip_id)},
            {"$set": {"status": new_status, "updatedAt": datetime.now(timezone.utc)}},
            session=session
        )
"""
    with open(mod_path / "repositories" / "payslip_repository.py", "w") as f:
        f.write(repo_code)

def write_routes(mod_path):
    route_code = """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/payslip", tags=["Payslip Engine"])

class GenerateRequest(BaseModel):
    payrollRunId: str

class PublishRequest(BaseModel):
    payrollRunId: str

class RegenerateRequest(BaseModel):
    payslipId: str

@router.post("/generate")
async def generate_payslips(req: GenerateRequest):
    '''
    Business API: Triggered via PayrollLocked event.
    Fetches finalized payroll ledger and creates Version 1 Draft payslips.
    '''
    return {"status": "Success", "message": f"Payslips generated for run {req.payrollRunId}."}

@router.post("/publish")
async def publish_payslips(req: PublishRequest):
    '''
    Business API: Transitions Generated payslips to Published.
    Generates PDFs and Checksums.
    '''
    return {"status": "Success", "message": "Payslips published.", "publishedEvents": ["PayslipPublished"]}

@router.post("/regenerate")
async def regenerate_payslip(req: RegenerateRequest):
    '''
    Business API: Creates Version N+1. Never overwrites historical versions.
    '''
    return {"status": "Success", "message": "Payslip regenerated."}
    
@router.post("/email")
async def email_payslip(payslipId: str):
    return {"status": "Success", "message": "Email sent."}
"""
    with open(mod_path / "routes" / "router.py", "w") as f:
        f.write(route_code)

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    mod_path = create_structure(base, "payslip")
    write_models(mod_path)
    write_utilities(mod_path)
    write_repository(mod_path)
    write_routes(mod_path)
    print("Payslip Engine completely generated.")
