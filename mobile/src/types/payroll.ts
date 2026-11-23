export interface SalaryComponent {
  code: string;
  name: string;
  type: 'EARNING' | 'DEDUCTION';
  amount: number;
}

export interface PayslipRecord {
  id: string;
  month: number;
  year: number;
  monthName: string;
  grossEarnings: number;
  totalDeductions: number;
  netSalary: number;
  status: 'DRAFT' | 'PUBLISHED';
  earnings: SalaryComponent[];
  deductions: SalaryComponent[];
  paidDays: number;
  lossOfPayDays: number;
  paymentDate?: string;
}
