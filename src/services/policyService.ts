import { api } from '../lib/api';

export interface AttendancePolicy {
  shiftStartTime: string;
  shiftEndTime: string;
  saturdayShiftEndTime: string;
  graceMinutes: number;
  lateStartMinute: number;
  lateEndMinute: number;
  latePermissionStartMinute: number;
  latePermissionEndMinute: number;
  halfDayCutoffTime: string;
  monthlyPermissionHours: number;
  lateHalfDayThreshold: number;
  lateFullDayThreshold: number;
  lateIncrementThreshold: number;
  lopHalfDayHours: number;
  lopFullDayHours: number;
}

export async function getAttendancePolicy() {
  return api.get<AttendancePolicy>('/v1/policy/attendance/');
}

export async function updateAttendancePolicy(policy: AttendancePolicy) {
  return api.put<AttendancePolicy>('/v1/policy/attendance/', policy);
}

// V2 Attendance Policy (Assigned to Shifts)
export interface AttendancePolicyV2 {
  _id?: string;
  name: string;
  description?: string;
  graceInMinutes: number;
  graceOutMinutes: number;
  minHoursForFullDay: number;
  minHoursForHalfDay: number;
  absentHoursThreshold: number;
  lopHalfDayHours: number;
  lopFullDayHours: number;
  lateInThresholdMinutes: number;
  earlyOutThresholdMinutes: number;
  status?: string;
  isCurrent?: boolean;
}

export async function getAttendancePoliciesV2(): Promise<AttendancePolicyV2[]> {
  const res = await api.get<any>('/v2/attendance-policy/attendancePolicys/');
  return res?.data || res || [];
}

export async function createAttendancePolicyV2(policy: AttendancePolicyV2) {
  return api.post<AttendancePolicyV2>('/v2/attendance-policy/attendancePolicys/', policy);
}

export async function updateAttendancePolicyV2(id: string, policy: AttendancePolicyV2) {
  return api.put<AttendancePolicyV2>(`/v2/attendance-policy/attendancePolicys/${id}`, policy);
}

export async function deleteAttendancePolicyV2(id: string) {
  return api.delete(`/v2/attendance-policy/attendancePolicys/${id}`);
}
