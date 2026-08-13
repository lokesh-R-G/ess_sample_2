import { api } from '../lib/api';

export interface LeaveTypeConfig {
  code: string;
  name: string;
  enabled: boolean;
  annualEntitlement: number;
  carryForwardEnabled: boolean;
  carryForwardLimit: number;
  carryForwardType: string;
  expiryEnabled: boolean;
  expiryRule: string;
  joiningYearProrationEnabled: boolean;
  prorationRule: string;
  anniversaryEligibilityEnabled: boolean;
  zeroBalanceApprovalAllowed: boolean;
  lopEnabled: boolean;
}

export interface LeavePolicyV2 {
  id?: string;
  policyCode: string;
  name: string;
  description?: string;
  effectiveFrom: string;
  effectiveTo?: string;
  status?: string;
  version?: number;
  leaveTypes: LeaveTypeConfig[];
}

export async function getLeavePoliciesV2(): Promise<LeavePolicyV2[]> {
  const res = await api.get<any>('/v2/leave-policies');
  return res?.data || res || [];
}

export async function getActiveLeavePolicyV2(): Promise<LeavePolicyV2 | null> {
  try {
    return await api.get<LeavePolicyV2>('/v2/leave-policies/active');
  } catch (e) {
    return null;
  }
}

export async function createLeavePolicyV2(policy: LeavePolicyV2) {
  return api.post<LeavePolicyV2>('/v2/leave-policies', policy);
}
