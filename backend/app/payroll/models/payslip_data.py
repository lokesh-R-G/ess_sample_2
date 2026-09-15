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
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Employment
    department: str
    designation: str
    dateOfJoining: Optional[str] = None
    employmentType: Optional[str] = None
    
    # Payment & Bank
    paymentMode: Optional[str] = "Bank Transfer"
    bankName: Optional[str] = None
    accountNumberMasked: Optional[str] = None
    ifscCode: Optional[str] = None
    accountHolderName: Optional[str] = None
    
    # Attendance
    workingDays: float
    payableDays: float
    presentDays: Optional[float] = None
    absentDays: Optional[float] = None
    halfDays: Optional[float] = None
    
    # Leave
    approvedLeave: Optional[float] = None
    leaveByType: Optional[Dict[str, float]] = None
    historicalLeaveBalance: Optional[float] = None
    
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
