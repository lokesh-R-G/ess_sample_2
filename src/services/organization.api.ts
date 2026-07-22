import { api } from '../lib/api';

export const organizationApi = {
  getCompanies: async () => {
    const res = await api.get('/organization/companies');
    return res.data;
  },
  getBranches: async (companyId?: string) => {
    const res = await api.get('/organization/branches' + (companyId ? `?companyId=${companyId}` : ''));
    return res.data;
  },
  getDepartments: async (companyId?: string) => {
    const res = await api.get('/organization/departments' + (companyId ? `?companyId=${companyId}` : ''));
    return res.data;
  },
  getDesignations: async (companyId?: string, departmentId?: string) => {
    const params = new URLSearchParams();
    if (companyId) params.append('companyId', companyId);
    if (departmentId) params.append('departmentId', departmentId);
    const qs = params.toString();
    const res = await api.get('/organization/designations' + (qs ? `?${qs}` : ''));
    return res.data;
  }
};
