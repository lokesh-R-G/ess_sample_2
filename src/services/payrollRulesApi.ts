import {api} from '../lib/api';

export const payrollRulesApi = {
  // Payroll Settings
  getPayrollSettings: () => api.get('/v2/payroll/payroll-settings/'),
  createPayrollSettings: (data: any) => api.post('/v2/payroll/payroll-settings/', data),
  updatePayrollSettings: (id: string, data: any) => api.put(`/v2/payroll/payroll-settings/${id}`, data),

  // PF Rules
  getPFRules: () => api.get('/v2/payroll/pf-rules/'),
  createPFRule: (data: any) => api.post('/v2/payroll/pf-rules/', data),
  updatePFRule: (id: string, data: any) => api.put(`/v2/payroll/pf-rules/${id}`, data),

  // ESI Rules
  getESIRules: () => api.get('/v2/payroll/esi-rules/'),
  createESIRule: (data: any) => api.post('/v2/payroll/esi-rules/', data),
  updateESIRule: (id: string, data: any) => api.put(`/v2/payroll/esi-rules/${id}`, data),

  // PT Rules
  getPTRules: () => api.get('/v2/payroll/pt-rules/'),
  createPTRule: (data: any) => api.post('/v2/payroll/pt-rules/', data),
  updatePTRule: (id: string, data: any) => api.put(`/v2/payroll/pt-rules/${id}`, data),

  // Component Behavior is part of Salary Component generic route
  getSalaryComponents: () => api.get('/v2/organization/salary-components/'),
  updateSalaryComponent: (id: string, data: any) => api.put(`/v2/organization/salary-components/${id}`, data),
};
