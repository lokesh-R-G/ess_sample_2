import { api } from '../lib/api';

export interface AdminSummary {
  stats: {
    totalEmployees: number;
    activeEmployees: number;
    newJoinees: number;
    attrition: number;
    attendanceRate: number;
    branches: number;
  };
  branchData: Array<{ id: string; name: string; city: string; employees: number; status: 'active' | 'inactive' }>;
  employeeList: Array<{ id: string; name: string; designation: string; status: 'active' | 'inactive' }>;
  attendanceTrend: { months: string[]; present: number[]; absent: number[] };
}

export async function getAdminSummary() {
  return api.get<AdminSummary>('/v1/admin/summary/');
}

export interface InviteEmployeePayload {
  employeeId: string;     // V2 UUID
  employeeCode: string;   // HR-assigned business code
  email: string;          // Personal email for welcome notification
  role: 'Employee' | 'Manager' | 'Admin';
}

export interface InviteEmployeeResponse {
  success: boolean;
  empId: string;
  employeeId: string;
  username: string;
  essStatus: string;
  emailSent: boolean;
}

export async function inviteEmployee(payload: InviteEmployeePayload) {
  return api.post<InviteEmployeeResponse>('/v1/admin/invite-employee/', payload);
}

/** @deprecated Use inviteEmployee() instead */
export async function createUser(empId: string, name?: string, force?: boolean) {
  return api.post('/v1/admin/create-user/', { empId, name, force });
}


export interface AttendanceSummary {
  present: number;
  absent: number;
  od: number;
}

export async function getAttendanceSummary() {
  return api.get<AttendanceSummary>('/v1/admin/attendance-summary/');
}
