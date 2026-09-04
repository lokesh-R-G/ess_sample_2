import { api } from '../lib/api';

export interface AttendanceRecord {
  empId: string;
  date: string;
  inTime?: string | null;
  outTime?: string | null;
  workHours?: number;
  status: 'present' | 'absent' | 'leave' | 'weekoff' | 'od' | 'partial' | string;
  lateMinutes?: number;
  lateCount?: number;
  lopHours?: number;
  halfDayCount?: number;
  
  // V2 Specific fields
  scheduleType?: string;
  scheduleSource?: string;
  actualStartTime?: string | null;
  actualEndTime?: string | null;
  lopReason?: string | null;
  monthlyLateCount?: number;
  breakDuration?: number;
  virtualBreakApplied?: boolean;
  lateIncrementApplied?: boolean;
  engineVersion?: string;
  processedAt?: string;
  
  // Snapshots
  shiftSnapshot?: any;
  attendancePolicySnapshot?: any;
  weeklyOffSnapshot?: any;
  holidaySnapshot?: any;
  approvalSnapshot?: any[];
  rawAttendanceLogIds?: string[];
  
  // Legacy fields (optional if backend still supplies them, but frontend won't rely on them for logic)
  firstIn?: string | null;
  lastOut?: string | null;
  punchCount?: number;
  workedMinutes?: number;
  permissionHoursUsed?: number;
  permissionHoursExceeded?: number;
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

export interface MobilePunchRequest {
  punchType: 'IN' | 'OUT';
  occurredAt: string;
  clientEventId: string;
  latitude?: number | null;
  longitude?: number | null;
  locationAccuracy?: number | null;
  deviceId?: string | null;
}

export interface MobilePunchResponse {
  status: string;
  punchId: string;
  punchType: 'IN' | 'OUT';
  occurredAt: string;
  serverReceivedAt: string;
  source: string;
  isNew: boolean;
}

export interface MobilePunch {
  punchId: string;
  punchType: 'IN' | 'OUT';
  occurredAt: string;
  source: string;
  location?: any;
}

export interface MobilePunchesTodayResponse {
  empId: string;
  records: MobilePunch[];
}

export async function submitMobilePunch(payload: MobilePunchRequest) {
  return api.post<MobilePunchResponse>('/v2/attendance/mobile/punch', payload);
}

export async function getTodayPunches() {
  return api.get<MobilePunchesTodayResponse>('/v2/attendance/mobile/punches/today');
}
