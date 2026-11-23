export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  ChangePassword: { forced?: boolean };
  MobilePunch: undefined;
  ApplyLeave: undefined;
  PayslipDetail: { payslipId: string };
  Notifications: undefined;
  Reimbursements: undefined;
  AdminDashboard: undefined;
  AdminEmployees: undefined;
  AdminLeaveApprovals: undefined;
  AdminReimbursementApprovals: undefined;
  AdminAttendanceMonitor: undefined;
  AdminPayrollCycles: undefined;
};

export type MainTabParamList = {
  DashboardTab: undefined;
  AttendanceTab: undefined;
  LeaveTab: undefined;
  PayrollTab: undefined;
  ProfileTab: undefined;
};
