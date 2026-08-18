import { api } from '../lib/api';

export interface PayrollCycle {
  id: string;
  companyId: string;
  name: string;
  startDate: string;
  endDate: string;
  processingStatus: string;
}

export const payrollCycleApi = {
  getCycles: async (): Promise<PayrollCycle[]> => {
    return api.get<PayrollCycle[]>('/payrollRun/cycles');
  },
  
  createCycle: async (data: any): Promise<PayrollCycle> => {
    return api.post<PayrollCycle>('/payrollRun/cycles', data);
  },
  
  updateStatus: async (cycleId: string, status: string): Promise<PayrollCycle> => {
    return api.patch<PayrollCycle>(`/payrollRun/cycles/${cycleId}/status`, { status });
  },

  calculatePayroll: async (cycleId: string): Promise<any> => {
    return api.post<any>(`/payrollRun/cycles/${cycleId}/process`, {});
  },
  
  recalculateEmployee: async (cycleId: string, employeeId: string, reason: string): Promise<any> => {
    return api.post<any>(`/payrollRun/cycles/${cycleId}/employees/${employeeId}/recalculate?reason=${reason}`);
  },

  exportCsv: async (cycleId: string): Promise<any> => {
    const res = await api.get<{csv: string}>(`/payrollRun/cycles/${cycleId}/export/csv`);
    return res.csv;
  }
};
