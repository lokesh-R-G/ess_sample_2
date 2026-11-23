import { api } from '../api/client';
import { AttendanceRecord, AttendanceSummary, PunchRequest } from '../types/attendance';

export async function getMyAttendance(month?: number, year?: number): Promise<{ records: AttendanceRecord[]; summary: AttendanceSummary }> {
  const query = month && year ? `?month=${month}&year=${year}` : '';
  const [records, summary] = await Promise.all([
    api.get<AttendanceRecord[]>(`/v2/attendance/my-records/${query}`).catch(() => []),
    api.get<AttendanceSummary>(`/v2/attendance/my-summary/${query}`).catch(() => ({
      totalDays: 0,
      presentDays: 0,
      absentDays: 0,
      halfDays: 0,
      weeklyOffs: 0,
      holidays: 0,
      leaveDays: 0,
      lateArrivals: 0,
      earlyDepartures: 0,
    }))
  ]);

  return { records, summary };
}

export async function submitPunch(data: PunchRequest): Promise<{ success: boolean; message: string }> {
  return api.post<{ success: boolean; message: string }>('/v2/attendance/punch/', data);
}

export async function requestRegularization(data: { date: string; reason: string; requestedInTime?: string; requestedOutTime?: string }): Promise<{ success: boolean }> {
  return api.post<{ success: boolean }>('/v2/attendance/regularization/', data);
}
