from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PayslipData(BaseModel):
    # Company & Org
    companyName: str
    companyAddress: Optional[str] = None
    branchName: str
    payrollMonth: str
    periodStart: str
    periodEnd: str
    
    # Employee Details
    employeeId: str
    employeeCode: str
    employeeName: str
    fatherHusbandName: Optional[str] = "-"
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[str] = "-"
    
    # Employment
    department: str
    designation: str
    dateOfJoining: Optional[str] = "-"
    employmentType: Optional[str] = None
    
    # Payment & Bank
    paymentMode: Optional[str] = "Bank Transfer"
    bankName: Optional[str] = "-"
    accountNumberMasked: Optional[str] = "-"
    ifscCode: Optional[str] = "-"
    accountHolderName: Optional[str] = "-"
    
    # Statutory
    uan: Optional[str] = "-"
    pan: Optional[str] = "-"
    
    # Attendance
    workingDays: float
    payableDays: float
    presentDays: Optional[float] = None
    absentDays: Optional[float] = None
    halfDays: Optional[float] = None
    
    # Leave Details
    leaveDetails: Optional[List[Dict[str, Any]]] = None
    
    # LOP
    lopDays: float
    lopAmount: Optional[float] = None
    lopBreakdown: Optional[Dict[str, Any]] = None
    
    # Financials
    earnings: List[Dict[str, Any]]
    grossEarnings: float
    deductions: List[Dict[str, Any]]
    grossDeductions: float
    netPay: float
    netPayWords: Optional[str] = None
    
    # Employer Contributions
    employerContributions: Optional[List[Dict[str, Any]]] = None
