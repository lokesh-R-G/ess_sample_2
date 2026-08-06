import { api } from '../lib/api';

export const organizationApi = {
  getCompanies: async () => {
    return await api.get('/v2/organization/companies/?limit=500');
  },
  getBranches: async (companyId?: string) => {
    return await api.get('/v2/organization/branches/?limit=500' + (companyId ? `&companyId=${companyId}` : ''));
  },
  getDepartments: async (companyId?: string) => {
    return await api.get('/v2/organization/departments/?limit=500' + (companyId ? `&companyId=${companyId}` : ''));
  },
  getDesignations: async (companyId?: string, departmentId?: string) => {
    const params = new URLSearchParams({ limit: '500' });
    if (companyId) params.append('companyId', companyId);
    if (departmentId) params.append('departmentId', departmentId);
    return await api.get('/v2/organization/designations/?' + params.toString());
  },
  getShifts: async () => {
    return await api.get('/v2/organization/shifts/?limit=500');
  },
  getHolidays: async () => {
    return await api.get('/v2/organization/holidays/?limit=500');
  },
  getSalaryStructures: async () => {
    return await api.get('/v2/organization/salary-structures/?limit=500');
  },
  getSalaryComponents: async () => {
    return await api.get('/v2/organization/salary-components/?limit=500');
  },
  getESSLMachines: async () => {
    return await api.get('/v2/organization/essl-machines/?limit=500');
  }
};
