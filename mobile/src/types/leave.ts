export interface LeaveBalanceItem {
  leaveTypeId: string;
  leaveTypeName: string;
  code: string;
  totalAllocated: number;
  used: number;
  pending: number;
  available: number;
}

export interface LeaveApplication {
  id: string;
  leaveTypeId: string;
  leaveTypeName: string;
  startDate: string;
  endDate: string;
  isHalfDay?: boolean;
  halfDaySession?: 'FIRST_HALF' | 'SECOND_HALF';
  totalDays: number;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  appliedOn: string;
  approverRemarks?: string;
  approverName?: string;
}

export interface CreateLeaveRequest {
  leaveTypeId: string;
  startDate: string;
  endDate: string;
  reason: string;
  isHalfDay?: boolean;
  halfDaySession?: 'FIRST_HALF' | 'SECOND_HALF';
}
