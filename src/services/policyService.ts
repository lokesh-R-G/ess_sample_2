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
