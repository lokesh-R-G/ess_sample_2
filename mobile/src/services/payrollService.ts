import { api } from '../api/client';
import { PayslipRecord } from '../types/payroll';

export async function getMyPayslips(): Promise<PayslipRecord[]> {
  return api.get<PayslipRecord[]>('/v2/payroll/my-payslips/').catch(() => []);
}

export async function getPayslipDetail(payslipId: string): Promise<PayslipRecord> {
  return api.get<PayslipRecord>(`/v2/payroll/payslip/${payslipId}/`);
}
