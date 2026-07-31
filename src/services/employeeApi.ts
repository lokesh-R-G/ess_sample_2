import { api } from '../lib/api';

export const employeeApi = {
  // Base Employee
  createEmployee: (data: any) => api.post('/v2/employee/employees/', data),
  updateEmployee: (id: string, data: any) => api.put(`/v2/employee/employees/${id}`, data),
  
  // Personal
  createPersonal: (data: any) => api.post('/v2/employee/employeePersonals/', data),
  
  // Contact
  createContact: (data: any) => api.post('/v2/employee/employeeContacts/', data),
  
  // Address
  createAddress: (data: any) => api.post('/v2/employee/employeeAddresss/', data),
  
  // Employment History
  createEmployment: (data: any) => api.post('/v2/employee/employmentHistorys/', data),
  
  // Banking
  createBanking: (data: any) => api.post('/v2/employee/employeeBanks/', data),
  
  // Government IDs
  createGovernmentId: (data: any) => api.post('/v2/employee/employeeGovernmentIds/', data),
  
  // Payroll Config
  createPayrollConfig: (data: any) => api.post('/v2/employee/employeePayrollConfigs/', data),

  // Calculate Payslip Preview
  calculatePayslipPreview: (data: any) => api.post('/v2/payroll/calculate-preview', data)
};
