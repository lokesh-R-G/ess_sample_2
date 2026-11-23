export interface AttendanceRecord {
  id?: string;
  date: string;
  inTime?: string | null;
  outTime?: string | null;
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'WEEKLY_OFF' | 'HOLIDAY' | 'ON_DUTY';
  totalHours?: number | null;
  isLate?: boolean;
  isEarlyDeparture?: boolean;
  regularizationStatus?: 'PENDING' | 'APPROVED' | 'REJECTED' | null;
}

export interface AttendanceSummary {
  totalDays: number;
  presentDays: number;
  absentDays: number;
  halfDays: number;
  weeklyOffs: number;
  holidays: number;
  leaveDays: number;
  lateArrivals: number;
  earlyDepartures: number;
}

export interface PunchRequest {
  latitude?: number;
  longitude?: number;
  punchType: 'IN' | 'OUT';
  remarks?: string;
}
