import { api } from '../lib/api';

export interface DashboardSummary {
  employee: {
    empId: string;
    name: string;
    designation?: string;
    branch?: string;
  };
  attendance: {
    presentDays: number;
    absentDays: number;
    leaveBalance: number;
    currentSalary: number;
    workingHours: number;
  };
  attendanceTrendData: {
    months: string[];
    present: number[];
  };
  leaveBalance: Record<string, { total: number; used: number; balance: number }>;
  upcomingHolidays: Array<{ date: string; name: string; type: string }>;
  notifications: Array<{ id: string; title: string; message: string; type: string; time: string }>;
}

export async function getDashboardSummary() {
  return api.get<DashboardSummary>('/dashboard/me');
}
