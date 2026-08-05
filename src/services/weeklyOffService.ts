import { api } from '../lib/api';

export interface WeeklyOffDayRule {
  dayOfWeek: number;
  weekNumbers: number[];
}

export interface WeeklyOffPolicy {
  _id?: string;
  name: string;
  description?: string;
  rules: WeeklyOffDayRule[];
  status?: string;
  isCurrent?: boolean;
}

export async function getWeeklyOffPolicies(): Promise<WeeklyOffPolicy[]> {
  const res = await api.get<any>('/v2/attendance-policy/weekly-off-policy/');
  return res?.data || res || [];
}

export async function createWeeklyOffPolicy(policy: WeeklyOffPolicy) {
  return api.post<WeeklyOffPolicy>('/v2/attendance-policy/weekly-off-policy/', policy);
}

export async function updateWeeklyOffPolicy(id: string, policy: WeeklyOffPolicy) {
  return api.put<WeeklyOffPolicy>(`/v2/attendance-policy/weekly-off-policy/${id}`, policy);
}

export async function deleteWeeklyOffPolicy(id: string) {
  return api.delete(`/v2/attendance-policy/weekly-off-policy/${id}`);
}
