import { api } from '../lib/api';

export const organizationApi = {
  getCompanies: async () => {
    const res = await api.get('/v1/organization/companies/');
    return (res as any).data;
  },
  getBranches: async (companyId?: string) => {
    const res = await api.get('/v1/organization/branches/' + (companyId ? `?companyId=${companyId}` : ''));
    return (res as any).data;
  },
  getDepartments: async (companyId?: string) => {
    const res = await api.get('/v1/organization/departments/' + (companyId ? `?companyId=${companyId}` : ''));
    return (res as any).data;
  },
  getDesignations: async (companyId?: string, departmentId?: string) => {
    const params = new URLSearchParams();
    if (companyId) params.append('companyId', companyId);
    if (departmentId) params.append('departmentId', departmentId);
    const qs = params.toString();
    const res = await api.get('/v1/organization/designations/' + (qs ? `?${qs}` : ''));
    return (res as any).data;
  }
};
