import { api } from '../lib/api';

export interface PayslipHistoryItem {
  month: string;
  netPay: number;
  status: string;
}

export interface PayslipDetails {
  month: string;
  employee: {
    name: string;
    employeeId: string;
    designation: string;
    department: string;
    branch: string;
    pan?: string;
    uan?: string;
    bankAccount?: string;
  };
  attendance: {
    presentDays: number;
    paidDays: number;
    lossOfPay: number;
  };
  earnings: Record<string, number> & { gross: number };
  deductions: Record<string, number> & { total: number };
  netPay: number;
  netPayWords: string;
}

export interface PayslipResponse {
  current: PayslipDetails | null;
  history: PayslipHistoryItem[];
}

export async function getPayslips() {
  const response = await api.get<{ payslips: Array<Partial<PayslipDetails> & { month?: string; netPay?: number; status?: string }> }>('/v1/payslip/me/');
  const history = (response.payslips ?? []).map((payslip) => ({
    month: payslip.month ?? 'Unknown',
    netPay: payslip.netPay ?? 0,
    status: payslip.status ?? 'generated',
  }));

  const currentRecord = response.payslips?.[0];
  const current: PayslipDetails | null = currentRecord && currentRecord.employee && currentRecord.attendance && currentRecord.earnings && currentRecord.deductions
    ? {
        month: currentRecord.month ?? 'Current',
        employee: {
          name: currentRecord.employee.name ?? '',
          employeeId: currentRecord.employee.employeeId ?? '',
          designation: currentRecord.employee.designation ?? '',
          department: currentRecord.employee.department ?? '',
          branch: currentRecord.employee.branch ?? '',
          pan: currentRecord.employee.pan,
          uan: currentRecord.employee.uan,
          bankAccount: currentRecord.employee.bankAccount,
        },
        attendance: {
          presentDays: currentRecord.attendance.presentDays ?? 0,
          paidDays: currentRecord.attendance.paidDays ?? 0,
          lossOfPay: currentRecord.attendance.lossOfPay ?? 0,
        },
        earnings: {
          ...currentRecord.earnings,
          gross: currentRecord.earnings.gross ?? 0,
        } as Record<string, number> & { gross: number },
        deductions: {
          ...currentRecord.deductions,
          total: currentRecord.deductions.total ?? 0,
        } as Record<string, number> & { total: number },
        netPay: currentRecord.netPay ?? 0,
        netPayWords: currentRecord.netPayWords ?? '',
      }
    : null;

  return { current, history } satisfies PayslipResponse;
}
