import { api } from '../lib/api';

export interface AttendanceRecord {
  empId: string;
  date: string;
  firstIn?: string | null;
  lastOut?: string | null;
  inTime?: string | null;
  outTime?: string | null;
  punchCount?: number;
  workedMinutes?: number;
  workHours?: number;
  status: 'present' | 'absent' | 'leave' | 'weekoff' | 'od' | 'partial' | string;
  sourceLogFingerprints?: string[];
  lateMinutes?: number;
  lateCount?: number;
  permissionHoursUsed?: number;
  permissionHoursExceeded?: number;
  lopHours?: number;
  halfDayCount?: number;
}

export interface AttendanceResponse {
  empId: string;
  records: AttendanceRecord[];
}

export async function getMyAttendance(fromDate?: string, toDate?: string) {
  const searchParams = new URLSearchParams();
  if (fromDate) searchParams.set('fromDate', fromDate);
  if (toDate) searchParams.set('toDate', toDate);
  const query = searchParams.toString();
  return api.get<AttendanceResponse>(`/v1/attendance/me/${query ? `?${query}` : ''}`);
}

export async function getAttendanceForEmployee(empId: string, fromDate?: string, toDate?: string) {
  const searchParams = new URLSearchParams();
  if (fromDate) searchParams.set('fromDate', fromDate);
  if (toDate) searchParams.set('toDate', toDate);
  const query = searchParams.toString();
  return api.get<AttendanceResponse>(`/v1/attendance/${empId}/${query ? `?${query}` : ''}`);
}

export interface RecalculateRequestPayload {
  fromDate: string;
  toDate: string;
  force: boolean;
}

export interface RecalculateResponse {
  success: boolean;
  engineVersion: string;
  fromDate: string;
  toDate: string;
  employeesProcessed: number;
  daysProcessed: number;
  attendanceRecordsCreated: number;
  attendanceRecordsUpdated: number;
  durationMs: number;
  errors: any[];
}

export async function recalculateAttendance(payload: RecalculateRequestPayload) {
  return api.post<RecalculateResponse>('/v2/attendance/recalculate', payload);
}
