import { api } from '../lib/api';
import {
  contactMapper,
  employmentMapper,
  payrollConfigMapper,
  EmployeeContactUI,
  EmploymentHistoryUI,
  EmployeePayrollConfigUI
} from './employeeMappers';

export const employeeApi = {
  // Base Employee
  getEmployees: () => api.get('/v2/employee/employees/'),
  getEmployee: (id: string) => api.get(`/v2/employee/employees/${id}`),
  createEmployee: (data: any) => api.post('/v2/employee/employees/', data),
  updateEmployee: (id: string, data: any) => api.put(`/v2/employee/employees/${id}`, data),
  
  // Personal
  getPersonal: (employeeId: string) => api.get(`/v2/employee/employeePersonals/?employeeId=${employeeId}`),
  createPersonal: (data: any) => api.post('/v2/employee/employeePersonals/', data),
  
  // Contact
  getContact: async (employeeId: string): Promise<EmployeeContactUI[]> => {
    const res = await api.get(`/v2/employee/employeeContacts/?employeeId=${employeeId}`);
    const data = res?.data || res || [];
    return Array.isArray(data) ? data.map(contactMapper.fromBackend) : [contactMapper.fromBackend(data)];
  },
  createContact: (data: EmployeeContactUI) => {
    const payload = contactMapper.toBackend(data);
    return api.post('/v2/employee/employeeContacts/', payload);
  },
  
  // Address
  getAddress: (employeeId: string) => api.get(`/v2/employee/employeeAddresss/?employeeId=${employeeId}`),
  createAddress: (data: any) => api.post('/v2/employee/employeeAddresss/', data),
  
  // Employment History
  getEmployment: async (employeeId: string): Promise<EmploymentHistoryUI[]> => {
    const res = await api.get(`/v2/employee/employmentHistorys/?employeeId=${employeeId}`);
    const data = res?.data || res || [];
    return Array.isArray(data) ? data.map(employmentMapper.fromBackend) : [employmentMapper.fromBackend(data)];
  },
  createEmployment: (data: EmploymentHistoryUI) => {
    const payload = employmentMapper.toBackend(data);
    return api.post('/v2/employee/employmentHistorys/', payload);
  },
  
  // Banking
  getBanking: (employeeId: string) => api.get(`/v2/employee/employeeBanks/?employeeId=${employeeId}`),
  createBanking: (data: any) => api.post('/v2/employee/employeeBanks/', data),
  
  // Government IDs
  getGovernmentId: (employeeId: string) => api.get(`/v2/employee/employeeGovernmentIds/?employeeId=${employeeId}`),
  createGovernmentId: (data: any) => api.post('/v2/employee/employeeGovernmentIds/', data),
  
  // Payroll Config
  getPayrollConfig: async (employeeId: string): Promise<EmployeePayrollConfigUI[]> => {
    const res = await api.get(`/v2/employee/employeePayrollConfigs/?employeeId=${employeeId}`);
    const data = res?.data || res || [];
    return Array.isArray(data) ? data.map(payrollConfigMapper.fromBackend) : [payrollConfigMapper.fromBackend(data)];
  },
  createPayrollConfig: (data: EmployeePayrollConfigUI) => {
    const payload = payrollConfigMapper.toBackend(data);
    return api.post('/v2/employee/employeePayrollConfigs/', payload);
  },

  // Calculate Payslip Preview
  calculateGross(payload: any) {
      return api.post('/v2/payroll/calculate-gross', payload);
  },
  calculatePayslipPreview: (data: any) => api.post('/v2/payroll/calculate-preview', data),

  // Assign Salary & Store Snapshot
  assignSalary: (data: any) => api.post('/v2/payroll/assign', data)
};
