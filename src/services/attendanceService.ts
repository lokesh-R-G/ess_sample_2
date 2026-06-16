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
  return api.get<AttendanceResponse>(`/attendance/me${query ? `?${query}` : ''}`);
}

export async function getAttendanceForEmployee(empId: string, fromDate?: string, toDate?: string) {
  const searchParams = new URLSearchParams();
  if (fromDate) searchParams.set('fromDate', fromDate);
  if (toDate) searchParams.set('toDate', toDate);
  const query = searchParams.toString();
  return api.get<AttendanceResponse>(`/attendance/${empId}${query ? `?${query}` : ''}`);
}
