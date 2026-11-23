export interface ReimbursementClaim {
  id: string;
  claimNumber: string;
  category: string;
  title: string;
  amount: number;
  claimDate: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'DISBURSED';
  description?: string;
  receiptUrl?: string;
  approverRemarks?: string;
}

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  category?: string;
  isRead: boolean;
  createdAt: string;
  actionUrl?: string;
}

export interface AdminSummaryStats {
  totalEmployees: number;
  presentToday: number;
  absentToday: number;
  onLeaveToday: number;
  pendingLeaveApprovals: number;
  pendingReimbursements: number;
}
