import { api } from '../lib/api';

export interface DashboardSummary {
  employee: {
    empId: string;
    name: string;
    designation?: string;
    branch?: string;
  };
  stats: {
    presentDays: number;
    absentDays: number;
    leaveBalance: number;
    currentSalary: number;
    workingHours: number;
  };
  attendance: Array<{
    date: string;
    firstIn?: string | null;
    lastOut?: string | null;
    punchCount?: number;
    workedMinutes?: number;
    status: 'present' | 'absent' | 'leave' | 'weekoff' | 'od' | 'partial';
  }>;
  distribution: number[];
  attendanceTrendData: {
    months: string[];
    present: number[];
  };
  notifications: Array<{ id?: string; title?: string; message?: string; type?: string; time?: string }>;
  holidays: Array<unknown>;
  leaveBalance: Record<string, { total: number; used: number; balance: number }>;
  upcomingHolidays: Array<{ date: string; name: string; type: string }>;
  alerts?: Array<{ type: 'success' | 'warning' | 'error' | 'info'; message: string }>;
}

export async function getDashboardSummary() {
  return api.get<DashboardSummary>('/dashboard/me');
}
