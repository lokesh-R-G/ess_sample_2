import { api } from '../lib/api';

export interface CompanySalaryBank {
  _id?: string;
  companyCode: string;
  accountHolderName: string;
  bankName: string;
  accountNumber: string;
  ifscCode: string;
  branchName?: string;
  accountType?: string;
  status: 'Active' | 'Inactive';
  isPrimary: boolean;
  updatedAt?: string;
}

export const companySalaryBankService = {
  getAll: async (companyCode?: string): Promise<CompanySalaryBank[]> => {
    const params = new URLSearchParams();
    if (companyCode) params.append('companyCode', companyCode);
    const response = await api.get<CompanySalaryBank[]>('/v2/payroll/company-salary-banks?' + params.toString());
    return response;
  },

  getByCompanyCode: async (companyCode: string): Promise<CompanySalaryBank[]> => {
    return api.get<CompanySalaryBank[]>(`/v2/payroll/company-salary-banks/company/${companyCode}`);
  },

  create: async (data: Omit<CompanySalaryBank, '_id' | 'updatedAt'>): Promise<CompanySalaryBank> => {
    return api.post<CompanySalaryBank>('/v2/payroll/company-salary-banks/', data);
  },

  update: async (id: string, data: Partial<CompanySalaryBank>): Promise<CompanySalaryBank> => {
    return api.put<CompanySalaryBank>(`/v2/payroll/company-salary-banks/${id}`, data);
  },

  setPrimary: async (id: string): Promise<CompanySalaryBank> => {
    return api.put<CompanySalaryBank>(`/v2/payroll/company-salary-banks/${id}/primary`);
  },
};
