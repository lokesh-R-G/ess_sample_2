import { api } from '../lib/api';

export interface PayrollCycle {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  processingStatus: string;
}

export interface AttendanceLedgerRow {
  employeeId: string;
  employeeCode?: string;
  employeeName: string;
  branchId?: string;
  branchName?: string;
  presentDays: number;
  absentDays: number;
  paidLeave: number;
  lop: number;
  workingDays: number;
  holiday: number;
  weeklyOff: number;
  attendanceStatus: string;
  dateFrom: string;
  dateTo: string;
}

export const payrollCycleApi = {
  getCycles: async (): Promise<PayrollCycle[]> => {
    return api.get<PayrollCycle[]>('/v2/payroll/cycles');
  },
  
  createCycle: async (data: any): Promise<PayrollCycle> => {
    return api.post<PayrollCycle>('/v2/payroll/cycles', data);
  },
  
  updateStatus: async (cycleId: string, status: string): Promise<PayrollCycle> => {
    return api.patch<PayrollCycle>(`/v2/payroll/cycles/${cycleId}/status`, { status });
  },

  calculatePayroll: async (cycleId: string, companyId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/process`, { companyId });
  },
  
  publishCycle: async (cycleId: string, companyId: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/publish`, { companyId });
  },
  
  recalculateEmployee: async (cycleId: string, employeeId: string, reason: string): Promise<any> => {
    return api.post<any>(`/v2/payroll/cycles/${cycleId}/employees/${employeeId}/recalculate?reason=${reason}`);
  },

  getAttendanceLedger: async (cycleId: string, companyId: string, branchId?: string): Promise<AttendanceLedgerRow[]> => {
    const params = new URLSearchParams({ companyId });
    if (branchId) params.append('branchId', branchId);
    return api.get<AttendanceLedgerRow[]>(`/v2/payroll/cycles/${cycleId}/attendance-ledger?${params.toString()}`);
  },

  exportCsv: async (cycleId: string, companyId: string): Promise<any> => {
    const res = await api.get<{csv: string}>(`/v2/payroll/cycles/${cycleId}/export/csv?companyId=${encodeURIComponent(companyId)}`);
    return res.csv;
  }
};
