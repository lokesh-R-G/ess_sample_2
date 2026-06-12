// Employee Data
export const employeeData = {
  id: 'EMP-001',
  name: 'John Doe',
  email: 'john.doe@idscompany.com',
  phone: '+91 98765 43210',
  designation: 'Senior Software Engineer',
  department: 'Engineering',
  branch: 'Bangalore HQ',
  branchId: 'BR-001',
  joiningDate: '2021-03-15',
  reportingTo: 'Sarah Smith',
  employeeType: 'Full-Time',
  salary: 85000,
  bankDetails: {
    accountNumber: 'XXXX-XXXX-4521',
    bankName: 'HDFC Bank',
    ifscCode: 'HDFC0001234',
  },
  emergencyContact: {
    name: 'Jane Doe',
    relationship: 'Spouse',
    phone: '+91 98765 43211',
  },
  address: '123, Green Valley, Bangalore - 560001',
};

// Attendance Stats
export const attendanceStats = {
  presentDays: 22,
  absentDays: 1,
  leaveDays: 2,
  weeklyOffs: 4,
  odDays: 1,
  totalDays: 30,
  attendancePercentage: 91.67,
  avgCheckIn: '09:15 AM',
  avgCheckOut: '06:45 PM',
  totalWorkingHours: 176,
};

// Monthly Attendance Data
export const monthlyAttendance = [
  { date: '2024-01-01', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-02', status: 'present', checkIn: '09:10', checkOut: '18:30', hours: 9.33 },
  { date: '2024-01-03', status: 'present', checkIn: '09:05', checkOut: '18:45', hours: 9.67 },
  { date: '2024-01-04', status: 'present', checkIn: '09:20', checkOut: '18:15', hours: 8.92 },
  { date: '2024-01-05', status: 'present', checkIn: '09:00', checkOut: '18:00', hours: 9 },
  { date: '2024-01-06', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-07', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-08', status: 'present', checkIn: '09:15', checkOut: '18:20', hours: 9.08 },
  { date: '2024-01-09', status: 'present', checkIn: '09:00', checkOut: '18:45', hours: 9.75 },
  { date: '2024-01-10', status: 'leave', checkIn: null, checkOut: null },
  { date: '2024-01-11', status: 'leave', checkIn: null, checkOut: null },
  { date: '2024-01-12', status: 'present', checkIn: '09:10', checkOut: '18:00', hours: 8.83 },
  { date: '2024-01-13', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-14', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-15', status: 'present', checkIn: '09:25', checkOut: '18:30', hours: 9.08 },
  { date: '2024-01-16', status: 'present', checkIn: '09:05', checkOut: '18:10', hours: 9.08 },
  { date: '2024-01-17', status: 'od', checkIn: null, checkOut: null, notes: 'Client Visit' },
  { date: '2024-01-18', status: 'present', checkIn: '09:00', checkOut: '18:45', hours: 9.75 },
  { date: '2024-01-19', status: 'present', checkIn: '09:10', checkOut: '18:00', hours: 8.83 },
  { date: '2024-01-20', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-21', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-22', status: 'present', checkIn: '09:15', checkOut: '18:20', hours: 9.08 },
  { date: '2024-01-23', status: 'present', checkIn: '09:00', checkOut: '18:45', hours: 9.75 },
  { date: '2024-01-24', status: 'present', checkIn: '09:10', checkOut: '18:30', hours: 9.33 },
  { date: '2024-01-25', status: 'absent', checkIn: null, checkOut: null },
  { date: '2024-01-26', status: 'present', checkIn: '09:05', checkOut: '18:00', hours: 8.92 },
  { date: '2024-01-27', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-28', status: 'weekoff', checkIn: null, checkOut: null },
  { date: '2024-01-29', status: 'present', checkIn: '09:10', checkOut: '18:15', hours: 9.08 },
  { date: '2024-01-30', status: 'present', checkIn: '09:00', checkOut: '18:30', hours: 9.5 },
  { date: '2024-01-31', status: 'present', checkIn: '09:15', checkOut: '18:00', hours: 8.75 },
];

// Leave Balance
export const leaveBalance = {
  annual: { total: 20, used: 5, balance: 15 },
  sick: { total: 10, used: 2, balance: 8 },
  casual: { total: 8, used: 3, balance: 5 },
  earned: { total: 12, used: 0, balance: 12 },
  compOff: { total: 4, used: 1, balance: 3 },
};

// Leave Applications
export const leaveApplications = [
  {
    id: 'LA-001',
    type: 'Annual Leave',
    fromDate: '2024-02-15',
    toDate: '2024-02-17',
    days: 3,
    reason: 'Family vacation',
    status: 'approved',
    appliedOn: '2024-02-01',
    approvedBy: 'Sarah Smith',
  },
  {
    id: 'LA-002',
    type: 'Sick Leave',
    fromDate: '2024-01-10',
    toDate: '2024-01-11',
    days: 2,
    reason: 'Medical appointment',
    status: 'approved',
    appliedOn: '2024-01-09',
    approvedBy: 'Sarah Smith',
  },
  {
    id: 'LA-003',
    type: 'Casual Leave',
    fromDate: '2024-03-01',
    toDate: '2024-03-01',
    days: 1,
    reason: 'Personal work',
    status: 'pending',
    appliedOn: '2024-02-20',
    approvedBy: null,
  },
  {
    id: 'LA-004',
    type: 'OD',
    fromDate: '2024-01-17',
    toDate: '2024-01-17',
    days: 1,
    reason: 'Client Visit',
    status: 'approved',
    appliedOn: '2024-01-15',
    approvedBy: 'Sarah Smith',
  },
];

// Payslip Data
export const payslipData = {
  month: 'January 2024',
  employee: {
    name: 'John Doe',
    employeeId: 'EMP-001',
    designation: 'Senior Software Engineer',
    department: 'Engineering',
    branch: 'Bangalore HQ',
    pan: 'ABCDE1234F',
    uan: '100234567890',
    bankAccount: 'XXXX-XXXX-4521',
  },
  attendance: {
    presentDays: 22,
    paidDays: 30,
    lossOfPay: 0,
  },
  earnings: {
    basic: 35000,
    hra: 15000,
    conveyance: 3000,
    medicalAllowance: 2500,
    specialAllowance: 12000,
    lta: 5000,
    bonus: 4000,
    gross: 76500,
  },
  deductions: {
    providentFund: 4200,
    professionalTax: 200,
    tds: 8000,
    healthInsurance: 2500,
    total: 14900,
  },
  netPay: 61600,
  netPayWords: 'Sixty-One Thousand Six Hundred Only',
};

// Previous Payslips
export const previousPayslips = [
  { month: 'January 2024', netPay: 61600, status: 'processed' },
  { month: 'December 2023', netPay: 61600, status: 'processed' },
  { month: 'November 2023', netPay: 60800, status: 'processed' },
  { month: 'October 2023', netPay: 61600, status: 'processed' },
  { month: 'September 2023', netPay: 60800, status: 'processed' },
  { month: 'August 2023', netPay: 61600, status: 'processed' },
];

// Upcoming Holidays
export const upcomingHolidays = [
  { date: '2024-03-08', name: 'Maha Shivaratri', type: 'Restricted' },
  { date: '2024-03-25', name: 'Holi', type: 'Gazetted' },
  { date: '2024-03-29', name: 'Good Friday', type: 'Restricted' },
  { date: '2024-04-14', name: 'Ambedkar Jayanti', type: 'Gazetted' },
  { date: '2024-04-21', name: 'Eid-ul-Fitr', type: 'Gazetted' },
  { date: '2024-05-01', name: 'Labour Day', type: 'Gazetted' },
];

// Notifications
export const notifications = [
  {
    id: 1,
    title: 'Leave Approved',
    message: 'Your leave request for Feb 15-17 has been approved.',
    type: 'success',
    time: '2m ago',
    read: false,
  },
  {
    id: 2,
    title: 'Payslip Generated',
    message: 'Your January 2024 payslip has been generated.',
    type: 'info',
    time: '1h ago',
    read: false,
  },
  {
    id: 3,
    title: 'Holiday Reminder',
    message: 'Holi holiday on March 25th. Enjoy!',
    type: 'warning',
    time: '2d ago',
    read: true,
  },
  {
    id: 4,
    title: 'Attendance Alert',
    message: 'You were marked absent on Jan 25th.',
    type: 'error',
    time: '1w ago',
    read: true,
  },
];

// Attendance Trend Data (for charts)
export const attendanceTrendData = {
  months: ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'],
  present: [22, 23, 21, 22, 24, 22],
  absent: [1, 0, 2, 1, 0, 1],
  leave: [2, 1, 1, 1, 2, 2],
};

// Leave Analysis Data (for charts)
export const leaveAnalysisData = {
  types: ['Annual', 'Sick', 'Casual', 'Earned', 'Comp Off'],
  used: [5, 2, 3, 0, 1],
  balance: [15, 8, 5, 12, 3],
};

// Dashboard Stats
export const dashboardStats = {
  presentDays: { value: 22, trend: 5, label: 'vs last month' },
  absentDays: { value: 1, trend: -50, label: 'vs last month' },
  leaveBalance: { value: 43, trend: 0, label: 'total remaining' },
  currentSalary: { value: 85000, trend: 10, label: 'annual hike' },
  workingHours: { value: 176, trend: 2, label: 'hrs this month' },
};

// Admin Data
export const adminStats = {
  totalEmployees: 245,
  activeEmployees: 238,
  newJoinees: 12,
  attrition: 5,
  attendanceRate: 94.2,
  pendingApprovals: 8,
  payrollProcessed: true,
  branches: 5,
};

export const branchData = [
  { id: 'BR-001', name: 'Bangalore HQ', employees: 120, city: 'Bangalore', status: 'active' },
  { id: 'BR-002', name: 'Mumbai Office', employees: 45, city: 'Mumbai', status: 'active' },
  { id: 'BR-003', name: 'Delhi NCR', employees: 38, city: 'New Delhi', status: 'active' },
  { id: 'BR-004', name: 'Chennai Branch', employees: 28, city: 'Chennai', status: 'active' },
  { id: 'BR-005', name: 'Hyderabad Office', employees: 14, city: 'Hyderabad', status: 'inactive' },
];

export const employeeList = [
  { id: 'EMP-001', name: 'John Doe', email: 'john.doe@idscompany.com', department: 'Engineering', designation: 'Senior Software Engineer', branch: 'Bangalore HQ', status: 'active', joiningDate: '2021-03-15' },
  { id: 'EMP-002', name: 'Jane Smith', email: 'jane.smith@idscompany.com', department: 'HR', designation: 'HR Manager', branch: 'Bangalore HQ', status: 'active', joiningDate: '2020-06-01' },
  { id: 'EMP-003', name: 'Mike Johnson', email: 'mike.j@idscompany.com', department: 'Sales', designation: 'Sales Lead', branch: 'Mumbai Office', status: 'active', joiningDate: '2022-01-10' },
  { id: 'EMP-004', name: 'Sarah Williams', email: 'sarah.w@idscompany.com', department: 'Marketing', designation: 'Marketing Manager', branch: 'Delhi NCR', status: 'active', joiningDate: '2021-08-20' },
  { id: 'EMP-005', name: 'David Brown', email: 'david.b@idscompany.com', department: 'Finance', designation: 'Accountant', branch: 'Bangalore HQ', status: 'active', joiningDate: '2023-02-15' },
  { id: 'EMP-006', name: 'Emily Davis', email: 'emily.d@idscompany.com', department: 'Engineering', designation: 'Frontend Developer', branch: 'Chennai Branch', status: 'active', joiningDate: '2022-07-01' },
  { id: 'EMP-007', name: 'Robert Wilson', email: 'robert.w@idscompany.com', department: 'Operations', designation: 'Operations Manager', branch: 'Bangalore HQ', status: 'inactive', joiningDate: '2020-04-01' },
  { id: 'EMP-008', name: 'Lisa Anderson', email: 'lisa.a@idscompany.com', department: 'Engineering', designation: 'QA Engineer', branch: 'Hyderabad Office', status: 'active', joiningDate: '2023-06-15' },
];
