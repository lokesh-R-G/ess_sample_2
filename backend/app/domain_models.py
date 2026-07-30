from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, List, Any
from pydantic import BaseModel, Field

class OrgBase(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

# ==========================================
# 1. ORGANIZATION ENGINE
# ==========================================

class Organization(OrgBase):
    name: str
    domain: str

class Company(OrgBase):
    organizationId: Optional[str] = None
    name: str
    registrationNumber: Optional[str] = None
    taxId: Optional[str] = None
    status: Literal["Active", "Inactive"] = "Active"

class ESSLMachine(OrgBase):
    serialNumber: str
    ipAddress: Optional[str] = None
    status: Literal["Active", "Offline", "Maintenance"] = "Active"
    lastSyncAt: Optional[datetime] = None

class Branch(OrgBase):
    companyId: str
    name: str
    code: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    contactDetails: Optional[str] = None
    attendanceEnabled: bool = True
    esslMachineId: Optional[str] = None
    timezone: str = "Asia/Kolkata"

class Department(OrgBase):
    companyId: str
    name: str
    code: Optional[str] = None
    headId: Optional[str] = None

class Designation(OrgBase):
    departmentId: str
    name: str
    level: int = 1

class Permission(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    resource: str
    action: str

class Role(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    name: str
    permissionIds: List[str] = []

class UserRole(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    roleId: str

class Shift(OrgBase):
    companyId: str
    name: str
    startTime: str
    endTime: str
    graceMinutes: int = 0
    workingHours: float = 8.0

class Holiday(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    branchId: Optional[str] = None
    name: str
    date: datetime
    isOptional: bool = False

# ==========================================
# 2. EMPLOYEE ENGINE
# ==========================================

class Employee(OrgBase):
    empId: str  # Kept for backward compatibility with eSSL
    firstName: str
    lastName: str
    email: str
    companyId: str
    branchId: Optional[str] = None
    departmentId: Optional[str] = None
    designationId: Optional[str] = None
    shiftId: Optional[str] = None
    managerId: Optional[str] = None
    joiningDate: Optional[datetime] = None
    status: Literal["Active", "Inactive", "Terminated", "On Leave"] = "Active"

class EmployeePersonal(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    maritalStatus: Optional[str] = None
    bloodGroup: Optional[str] = None

class EmployeeAddress(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    addressType: Literal["Current", "Permanent"]
    street: str
    city: str
    state: str
    zipCode: str
    country: str

class EmployeeBank(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    bankName: str
    accountNumber: str
    ifscCode: str
    accountType: str = "Savings"
    isPrimary: bool = True

class EmployeeFamily(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    name: str
    relation: str
    dob: Optional[datetime] = None
    contactNumber: Optional[str] = None

class EmployeeEducation(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    institution: str
    degree: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None

class EmployeeExperience(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    companyName: str
    role: str
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None

class EmploymentHistory(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    departmentId: str
    designationId: str
    managerId: Optional[str] = None
    startDate: datetime
    endDate: Optional[datetime] = None

class AuthUser(OrgBase):
    # Normalized auth table
    employeeId: str
    username: str
    passwordHash: str
    isActive: bool = True
    lastLogin: Optional[datetime] = None

# ==========================================
# 3. SALARY ENGINE
# ==========================================

class SalaryComponent(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    name: str
    code: Optional[str] = None
    componentType: Literal["Earning", "Deduction"]
    calculationMethod: Literal["Flat", "Percentage", "Formula"] = "Flat"
    defaultFormula: Optional[str] = None
    isTaxable: bool = True
    pfApplicability: bool = False
    esiApplicability: bool = False
    displayOrder: int = 1
    isActive: bool = True

class SalaryStructure(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    name: str
    description: Optional[str] = None

class SalaryStructureComponent(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    structureId: str
    componentId: str
    formula: Optional[str] = None

class EmployeeSalaryAssignment(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    structureId: str
    effectiveFrom: datetime
    effectiveTo: Optional[datetime] = None
    ctcAmount: float = 0.0
    baseAmount: float = 0.0

class EmployeeSalaryComponent(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    salaryComponentId: str
    monthlyAmount: float
    annualAmount: float
    formulaUsed: Optional[str] = None
    effectiveDate: datetime
    version: int = 1
    status: Literal["Active", "Archived"] = "Active"

class ComplianceConfig(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    complianceType: Literal["PF", "ESI", "PT", "LWF"]
    employeeContributionPercent: float = 0.0
    employerContributionPercent: float = 0.0
    maxLimit: float = 0.0
    effectiveDate: datetime

# ==========================================
# 4. LEAVE ENGINE
# ==========================================

class LeaveType(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    name: str
    code: str
    isPaid: bool = True
    accrualRate: float = 0.0

class LeaveTransaction(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    leaveTypeId: str
    transactionType: Literal["Accrual", "Deduction", "Grant"]
    amount: float
    date: datetime
    description: Optional[str] = None
    referenceId: Optional[str] = None

class LeaveRequest(OrgBase):
    employeeId: str
    leaveTypeId: str
    startDate: datetime
    endDate: datetime
    status: Literal["Pending", "Approved", "Rejected"] = "Pending"
    workflowId: Optional[str] = None

class LeaveBalance(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    leaveTypeId: str
    balance: float
    lastUpdated: datetime

# ==========================================
# 5. PAYROLL ENGINE
# ==========================================

class PayrollCycle(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    name: str
    startDate: datetime
    endDate: datetime
    processingStatus: Literal["Draft", "Processing", "Completed"] = "Draft"

class Payroll(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    cycleId: str
    employeeId: str
    grossEarnings: float = 0.0
    grossDeductions: float = 0.0
    netPay: float = 0.0
    status: Literal["Generated", "Paid"] = "Generated"

class PayrollLineItem(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    payrollId: str
    componentId: str
    itemType: Literal["Earning", "Deduction"]
    amount: float
    description: Optional[str] = None

# ==========================================
# 6. PAYSLIP ENGINE
# ==========================================

class Payslip(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    payrollId: str
    employeeId: str
    cycleId: str
    generatedDate: datetime
    pdfUrl: Optional[str] = None
    payloadSnapshot: dict = Field(default_factory=dict)

# ==========================================
# 7. AUDIT ENGINE
# ==========================================

class AuditLog(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: Optional[str] = None
    entity: str
    entityId: str
    action: Literal["Create", "Update", "Delete"]
    changes: List[Any] = []
    timestamp: datetime

# ==========================================
# 8. NOTIFICATION ENGINE
# ==========================================

class NotificationTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    channel: Literal["Email", "SMS", "Push"]
    subjectTemplate: Optional[str] = None
    bodyTemplate: str

class Notification(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    templateId: str
    status: Literal["Unread", "Read"] = "Unread"
    sentAt: datetime

class EmailQueue(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    toAddress: str
    subject: str
    body: str
    status: Literal["Pending", "Sent", "Failed"] = "Pending"
    retryCount: int = 0
