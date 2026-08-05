import { api } from '../lib/api';

export interface ShiftV2 {
  _id?: string;
  shiftCode: string;
  name: string;
  description?: string;
  attendancePolicyId: string;
  
  startTime: string;
  endTime: string;
  
  breakStartTime?: string;
  breakEndTime?: string;
  autoPunchLunchOut: boolean;
  autoPunchLunchIn: boolean;
  
  isCrossMidnight: boolean;
  
  version?: number;
  isCurrent?: boolean;
  effectiveFrom?: string;
  effectiveTo?: string;
  
  status?: string;
}

export async function getShiftsV2(): Promise<ShiftV2[]> {
  const res = await api.get<any>('/v2/organization/shifts/');
  return res?.data || res || [];
}

export async function createShiftV2(shift: ShiftV2) {
  return api.post<ShiftV2>('/v2/organization/shifts/', shift);
}

export async function updateShiftV2(id: string, shift: ShiftV2) {
  return api.put<ShiftV2>(`/v2/organization/shifts/${id}`, shift);
}

export async function deleteShiftV2(id: string) {
  return api.delete(`/v2/organization/shifts/${id}`);
}
