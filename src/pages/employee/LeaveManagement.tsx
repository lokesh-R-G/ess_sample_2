import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar as CalendarIcon, MapPin, Plus, Clock, CheckCircle, XCircle, AlertCircle, Send, FileText } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input, Select } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { DonutChart } from '../../components/charts';
import { createLeaveRequest, getLeaveData, LeaveApplication, LeaveBalanceItem } from '../../services/leaveService';
import { approvalService, PermissionLedger, ApprovalResponse } from '../../services/approvalService';
import { getActiveLeavePolicyV2, LeaveTypeConfig } from '../../services/leavePolicyService';
import { useAuth } from '../../context/AuthContext';

export const LeaveManagement: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'leave' | 'permission' | 'od' | 'misspunch' | 'history'>('leave');
  
  // V1 Leave State
  const [leaveBalance, setLeaveBalance] = useState<Record<string, LeaveBalanceItem>>({});
  const [leaveApplications, setLeaveApplications] = useState<LeaveApplication[]>([]);
  const [leaveAnalysisData, setLeaveAnalysisData] = useState<number[]>([0, 0, 0]);
  
  // M2.1 Approval State
  const [approvalRequests, setApprovalRequests] = useState<ApprovalResponse[]>([]);
  const [permissionLedger, setPermissionLedger] = useState<PermissionLedger | null>(null);

  // Modals & Form State
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [showPermissionModal, setShowPermissionModal] = useState(false);
  const [showOdModal, setShowOdModal] = useState(false);
  const [showMissPunchModal, setShowMissPunchModal] = useState(false);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Dynamic Leave Types
  const [leaveTypes, setLeaveTypes] = useState<LeaveTypeConfig[]>([]);

  // Form Data
  const [leaveFormData, setLeaveFormData] = useState({ leaveType: '', fromDate: '', toDate: '', reason: '' });
  const [permFormData, setPermFormData] = useState({ date: '', fromTime: '', toTime: '', reason: '' });
  const [odFormData, setOdFormData] = useState({ type: 'full', fromDate: '', toDate: '', fromTime: '', toTime: '', location: '', reason: '' });
  const [mpFormData, setMpFormData] = useState({ date: '', type: 'MISSING_IN', time: '', reason: '' }); // Miss Punch approval uses "Miss Punch"

  const loadAllData = async () => {
    setIsLoading(true);
    try {
      // Load V1 Leave
      const leaveRes = await getLeaveData();
      setLeaveBalance(leaveRes.leaveBalance ?? {});
      setLeaveApplications(leaveRes.requests ?? []);
      setLeaveAnalysisData(leaveRes.leaveAnalysisData ?? [0, 0, 0]);
      
      // Load V2 Approvals & Ledger
      if (user?.employeeId) {
        const [ledgerRes, approvalsRes, policyRes] = await Promise.all([
          approvalService.getPermissionLedger().catch(() => null),
          approvalService.getMyRequests(user.employeeId),
          getActiveLeavePolicyV2().catch(() => null)
        ]);
        setPermissionLedger(ledgerRes);
        setApprovalRequests(approvalsRes);
        if (policyRes) {
          setLeaveTypes(policyRes.leaveTypes.filter(lt => lt.enabled));
        } else {
          // Fallback if no active policy is found
          setLeaveTypes([]);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [user]);

  const handleLeaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!user?.employeeId) throw new Error("Employee ID missing");
      await createLeaveRequest({
        employeeId: user.employeeId,
        requestType: 'leave',
        leaveType: leaveFormData.leaveType,
        fromDate: leaveFormData.fromDate,
        toDate: leaveFormData.toDate,
        reason: leaveFormData.reason
      });
      await loadAllData();
      setShowLeaveModal(false);
      setLeaveFormData({ leaveType: '', fromDate: '', toDate: '', reason: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply leave');
    }
  };

  // V2 Permission Submission
  const handlePermissionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!user?.employeeId) throw new Error("Employee ID missing");
      await approvalService.submitApproval({
        employeeId: user.employeeId,
        approvalType: 'Permission',
        requestData: {
          date: permFormData.date,
          fromTime: permFormData.fromTime,
          toTime: permFormData.toTime
        },
        remarks: permFormData.reason
      });
      await loadAllData();
      setShowPermissionModal(false);
      setPermFormData({ date: '', fromTime: '', toTime: '', reason: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply permission');
    }
  };

  // V2 OD Submission
  const handleOdSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!user?.employeeId) throw new Error("Employee ID missing");
      const requestData: any = {
        fromDate: odFormData.fromDate,
        toDate: odFormData.toDate,
        location: odFormData.location
      };
      if (odFormData.type === 'partial') {
        requestData.fromTime = odFormData.fromTime;
        requestData.toTime = odFormData.toTime;
      }
      await approvalService.submitApproval({
        employeeId: user.employeeId,
        approvalType: 'On Duty',
        requestData,
        remarks: odFormData.reason
      });
      await loadAllData();
      setShowOdModal(false);
      setOdFormData({ type: 'full', fromDate: '', toDate: '', fromTime: '', toTime: '', location: '', reason: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply OD');
    }
  };

  // V2 Miss Punch Submission
  const handleMissPunchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!user?.employeeId) throw new Error("Employee ID missing");
      // Format to ISO if backend expects punchTime for synthetic punch
      const punchTimeStr = `${mpFormData.date}T${mpFormData.time}:00+05:30`;
      await approvalService.submitApproval({
        employeeId: user.employeeId,
        approvalType: 'Miss Punch',
        requestData: {
          punchTime: punchTimeStr,
          type: mpFormData.type
        },
        remarks: mpFormData.reason
      });
      await loadAllData();
      setShowMissPunchModal(false);
      setMpFormData({ date: '', type: 'MISSING_IN', time: '', reason: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply Miss Punch');
    }
  };

  const statusColors: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    APPROVED: 'success',
    PENDING: 'warning',
    REJECTED: 'error',
    CANCELLED: 'default',
    approved: 'success',
    pending: 'warning',
    rejected: 'error',
  };

  // Permission Duration display helper
  const calcDuration = (from: string, to: string) => {
    if (!from || !to) return 0;
    const [h1, m1] = from.split(':').map(Number);
    const [h2, m2] = to.split(':').map(Number);
    return (h2 * 60 + m2) - (h1 * 60 + m1);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {error && <GlassCard className="p-4 border border-red-200 bg-red-50 text-red-700">{error}</GlassCard>}
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h1 className="text-2xl font-bold text-neutral-900">Employee Requests</h1>
        </div>

        <motion.div className="flex flex-wrap items-center gap-2" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          {[
            { id: 'leave', label: 'Leave', icon: CalendarIcon },
            { id: 'permission', label: 'Permission', icon: Clock },
            { id: 'od', label: 'On Duty', icon: MapPin },
            { id: 'misspunch', label: 'Miss Punch', icon: AlertCircle },
            { id: 'history', label: 'Approval History', icon: FileText },
          ].map((tab) => (
            <motion.button key={tab.id} onClick={() => setActiveTab(tab.id as any)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id ? 'bg-primary-50 text-primary-600 border border-primary-300' : 'text-neutral-500 hover:bg-neutral-100 border border-transparent'}`}>
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </motion.button>
          ))}
          <div className="flex-1" />
          {activeTab === 'leave' && <AnimatedButton variant="primary" size="sm" icon={Plus} onClick={() => setShowLeaveModal(true)}>Apply Leave</AnimatedButton>}
          {activeTab === 'permission' && <AnimatedButton variant="primary" size="sm" icon={Plus} onClick={() => setShowPermissionModal(true)}>Request Permission</AnimatedButton>}
          {activeTab === 'od' && <AnimatedButton variant="primary" size="sm" icon={Plus} onClick={() => setShowOdModal(true)}>Request OD</AnimatedButton>}
          {activeTab === 'misspunch' && <AnimatedButton variant="primary" size="sm" className="bg-red-50 text-red-600 border-red-200" icon={Plus} onClick={() => setShowMissPunchModal(true)}>Miss Punch</AnimatedButton>}
        </motion.div>

        <AnimatePresence mode="wait">
          {activeTab === 'leave' && (
            <motion.div key="leave" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <GlassCard className="p-6 mb-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {Object.entries(leaveBalance).map(([key, value]) => (
                    <div key={key} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                      <p className="text-xs text-neutral-500 capitalize">{key}</p>
                      <div className="text-2xl font-bold">{value.balance} <span className="text-sm text-neutral-400">/ {value.total}</span></div>
                    </div>
                  ))}
                </div>
              </GlassCard>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold mb-4">Leave Applications</h3>
                <div className="space-y-3">
                  {leaveApplications.map((app) => (
                    <div key={app.id || app._id} className="flex justify-between items-center p-4 bg-neutral-50 rounded-xl border border-neutral-200">
                      <div>
                        <div className="font-medium">{app.requestData?.leaveType || 'Leave'} <StatusBadge status={statusColors[app.status]} label={app.status} size="sm" /></div>
                        <div className="text-sm text-neutral-500">{app.requestData?.fromDate} to {app.requestData?.toDate}</div>
                      </div>
                      <div className="text-xs text-neutral-400">{new Date(app.createdAt || Date.now()).toLocaleDateString()}</div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          )}

          {activeTab === 'permission' && (
            <motion.div key="permission" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <GlassCard className="p-6">
                    <h3 className="text-lg font-semibold mb-4">My Permission Requests</h3>
                    <div className="space-y-3">
                      {approvalRequests.filter(r => r.approvalType === 'Permission').map(app => (
                        <div key={app.id} className="flex justify-between items-center p-4 bg-neutral-50 rounded-xl border border-neutral-200">
                          <div>
                            <div className="font-medium">{app.requestData.date} <StatusBadge status={statusColors[app.status]} label={app.status} size="sm" /></div>
                            <div className="text-sm text-neutral-500">{app.requestData.fromTime} - {app.requestData.toTime} ({calcDuration(app.requestData.fromTime, app.requestData.toTime)} mins)</div>
                            <div className="text-xs italic text-neutral-500 mt-1">"{app.remarks}"</div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-neutral-400">Submitted: {app.createdAt ? new Date(app.createdAt).toLocaleDateString() : ''}</div>
                          </div>
                        </div>
                      ))}
                      {approvalRequests.filter(r => r.approvalType === 'Permission').length === 0 && (
                        <p className="text-sm text-neutral-500">No permission requests found.</p>
                      )}
                    </div>
                  </GlassCard>
                </div>
                <div>
                  <GlassCard className="p-6 sticky top-6">
                    <h3 className="text-lg font-semibold mb-4">Monthly Permission Ledger</h3>
                    {permissionLedger ? (
                      <div className="space-y-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Free Allowance</span>
                          <span className="font-medium text-emerald-600">{permissionLedger.freeAllowanceMinutes} min</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Used This Month</span>
                          <span className="font-medium">{permissionLedger.consumedMinutes} min</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Current Excess</span>
                          <span className="font-medium text-amber-600">{permissionLedger.currentExcessMinutes} min</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-neutral-500">Previous Carry</span>
                          <span className="font-medium">{permissionLedger.previousCarriedMinutes} min</span>
                        </div>
                        <div className="pt-3 border-t border-neutral-200 flex justify-between text-sm font-semibold">
                          <span>Accumulated Excess</span>
                          <span className={permissionLedger.accumulatedExcessMinutes >= permissionLedger.policyLimits.permissionLopThresholdMinutes ? 'text-red-600' : 'text-amber-600'}>
                            {permissionLedger.accumulatedExcessMinutes} min
                          </span>
                        </div>
                        
                        <div className="mt-6 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
                          <p className="text-xs font-semibold text-neutral-600 mb-2">Policy Limits</p>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <span className="text-neutral-500">Max per request:</span>
                            <span className="text-right font-medium">{permissionLedger.policyLimits.permissionMinutes} min</span>
                            <span className="text-neutral-500">Threshold:</span>
                            <span className="text-right font-medium">{permissionLedger.policyLimits.permissionLopThresholdMinutes} min</span>
                            <span className="text-neutral-500">LOP Value:</span>
                            <span className="text-right font-medium">{permissionLedger.policyLimits.permissionLopValue} Days</span>
                          </div>
                        </div>

                        {permissionLedger.lopGenerated > 0 && (
                          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                            <AlertCircle className="w-4 h-4 inline mr-2" />
                            <strong>{permissionLedger.lopGenerated} Day LOP</strong> generated from excess accumulation.
                          </div>
                        )}
                        {permissionLedger.accumulatedExcessMinutes >= permissionLedger.policyLimits.permissionLopThresholdMinutes && permissionLedger.lopGenerated === 0 && (
                          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                            <AlertCircle className="w-4 h-4 inline mr-2" />
                            Threshold reached! Submitting another request may generate LOP.
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-neutral-500">Ledger details unavailable.</p>
                    )}
                  </GlassCard>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'od' && (
            <motion.div key="od" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold mb-4">My On Duty (OD) Requests</h3>
                <div className="space-y-3">
                  {approvalRequests.filter(r => r.approvalType === 'On Duty').map(app => (
                    <div key={app.id} className="flex justify-between items-center p-4 bg-neutral-50 rounded-xl border border-neutral-200">
                      <div>
                        <div className="font-medium text-purple-700">On Duty <StatusBadge status={statusColors[app.status]} label={app.status} size="sm" /></div>
                        <div className="text-sm text-neutral-600">
                          {app.requestData.fromDate} to {app.requestData.toDate}
                          {app.requestData.fromTime && ` (${app.requestData.fromTime} - ${app.requestData.toTime})`}
                        </div>
                        <div className="text-xs text-neutral-500">Location: {app.requestData.location}</div>
                        <div className="text-xs italic text-neutral-500 mt-1">"{app.remarks}"</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-neutral-400">Submitted: {app.createdAt ? new Date(app.createdAt).toLocaleDateString() : ''}</div>
                      </div>
                    </div>
                  ))}
                  {approvalRequests.filter(r => r.approvalType === 'On Duty').length === 0 && (
                    <p className="text-sm text-neutral-500">No OD requests found.</p>
                  )}
                </div>
              </GlassCard>
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold mb-4">Unified Approval History (V2)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead>
                      <tr className="border-b border-neutral-200 text-neutral-500">
                        <th className="py-3 pr-4">ID</th>
                        <th className="py-3 px-4">Type</th>
                        <th className="py-3 px-4">Date(s)</th>
                        <th className="py-3 px-4">Time</th>
                        <th className="py-3 px-4">Reason</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Submitted</th>
                        <th className="py-3 px-4">Approved By</th>
                      </tr>
                    </thead>
                    <tbody>
                      {approvalRequests.map(app => (
                        <tr key={app.id} className="border-b border-neutral-100 hover:bg-neutral-50">
                          <td className="py-3 pr-4 text-xs font-mono text-neutral-400">..{app.id.slice(-6)}</td>
                          <td className="py-3 px-4 font-medium text-neutral-800">{app.approvalType}</td>
                          <td className="py-3 px-4 text-neutral-600">{app.requestData.date || app.requestData.fromDate} {app.requestData.toDate && app.requestData.toDate !== app.requestData.fromDate ? `to ${app.requestData.toDate}` : ''}</td>
                          <td className="py-3 px-4 text-neutral-600">{app.requestData.fromTime ? `${app.requestData.fromTime} - ${app.requestData.toTime}` : (app.approvalType === 'On Duty' ? 'Full Day' : '-')}</td>
                          <td className="py-3 px-4 text-neutral-600 truncate max-w-[200px]" title={app.remarks}>{app.remarks}</td>
                          <td className="py-3 px-4"><StatusBadge status={statusColors[app.status] || 'default'} label={app.status} size="sm" /></td>
                          <td className="py-3 px-4 text-neutral-500">{app.createdAt ? new Date(app.createdAt).toLocaleString() : ''}</td>
                          <td className="py-3 px-4 text-neutral-500">{app.approvedBy || '-'}</td>
                        </tr>
                      ))}
                      {approvalRequests.length === 0 && (
                        <tr><td colSpan={8} className="py-4 text-center text-neutral-500">No requests found.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </GlassCard>
            </motion.div>
          )}

          {activeTab === 'misspunch' && (
            <motion.div key="misspunch" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold mb-4">Miss Punch Requests (V2)</h3>
                <div className="space-y-3">
                  {approvalRequests.filter(r => r.approvalType === 'Miss Punch').map(app => (
                    <div key={app.id} className="flex justify-between items-center p-4 bg-neutral-50 rounded-xl border border-neutral-200">
                      <div>
                        <div className="font-medium text-red-700">Miss Punch <StatusBadge status={statusColors[app.status]} label={app.status} size="sm" /></div>
                        <div className="text-sm text-neutral-600">
                          {app.requestData.type} at {app.requestData.punchTime ? new Date(app.requestData.punchTime).toLocaleString() : ''}
                        </div>
                        <div className="text-xs italic text-neutral-500 mt-1">"{app.remarks}"</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-neutral-400">Submitted: {app.createdAt ? new Date(app.createdAt).toLocaleDateString() : ''}</div>
                      </div>
                    </div>
                  ))}
                  {approvalRequests.filter(r => r.approvalType === 'Miss Punch').length === 0 && (
                    <p className="text-sm text-neutral-500">No Miss Punch requests found.</p>
                  )}
                </div>
              </GlassCard>
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      {/* Leave Modal */}
      <Modal isOpen={showLeaveModal} onClose={() => setShowLeaveModal(false)} title="Apply Leave" size="md">
        <form onSubmit={handleLeaveSubmit} className="space-y-4">
          <Select label="Leave Type" options={
            leaveTypes.map(lt => ({value: lt.code, label: `${lt.name} (${lt.code})`}))
          } value={leaveFormData.leaveType} onChange={e => setLeaveFormData({...leaveFormData, leaveType: e.target.value})} required />
          <div className="grid grid-cols-2 gap-4">
            <Input label="From Date" type="date" value={leaveFormData.fromDate} onChange={e => setLeaveFormData({...leaveFormData, fromDate: e.target.value})} required />
            <Input label="To Date" type="date" value={leaveFormData.toDate} onChange={e => setLeaveFormData({...leaveFormData, toDate: e.target.value})} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Reason</label>
            <textarea className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20" rows={3} value={leaveFormData.reason} onChange={e => setLeaveFormData({...leaveFormData, reason: e.target.value})} required />
          </div>
          <div className="flex gap-3 pt-2">
            <AnimatedButton type="button" variant="ghost" fullWidth onClick={() => setShowLeaveModal(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" variant="primary" fullWidth icon={Send}>Submit Leave</AnimatedButton>
          </div>
        </form>
      </Modal>

      {/* Permission Modal */}
      <Modal isOpen={showPermissionModal} onClose={() => setShowPermissionModal(false)} title="Request Permission" size="md">
        <form onSubmit={handlePermissionSubmit} className="space-y-4">
          <Input label="Date" type="date" value={permFormData.date} onChange={e => setPermFormData({...permFormData, date: e.target.value})} required />
          <div className="grid grid-cols-2 gap-4">
            <Input label="From Time" type="time" value={permFormData.fromTime} onChange={e => setPermFormData({...permFormData, fromTime: e.target.value})} required />
            <Input label="To Time" type="time" value={permFormData.toTime} onChange={e => setPermFormData({...permFormData, toTime: e.target.value})} required />
          </div>
          {permFormData.fromTime && permFormData.toTime && (
            <div className="text-sm text-neutral-500">
              Duration: <span className="font-medium text-neutral-900">{calcDuration(permFormData.fromTime, permFormData.toTime)} mins</span>
            </div>
          )}
          
          {permissionLedger && permissionLedger.accumulatedExcessMinutes >= permissionLedger.policyLimits.permissionLopThresholdMinutes && (
             <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                <AlertCircle className="w-4 h-4 inline mr-2" />
                <strong>Warning:</strong> You have reached your permission threshold. This request may generate LOP.
             </div>
          )}

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Reason</label>
            <textarea className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20" rows={3} value={permFormData.reason} onChange={e => setPermFormData({...permFormData, reason: e.target.value})} required />
          </div>
          <div className="flex gap-3 pt-2">
            <AnimatedButton type="button" variant="ghost" fullWidth onClick={() => setShowPermissionModal(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" variant="primary" fullWidth icon={Send}>Submit Permission</AnimatedButton>
          </div>
        </form>
      </Modal>

      {/* OD Modal */}
      <Modal isOpen={showOdModal} onClose={() => setShowOdModal(false)} title="Request On Duty (OD)" size="md">
        <form onSubmit={handleOdSubmit} className="space-y-4">
          <Select label="OD Type" options={[
            {value: 'full', label: 'Full Day'},
            {value: 'partial', label: 'Partial Day'}
          ]} value={odFormData.type} onChange={e => setOdFormData({...odFormData, type: e.target.value})} />
          
          <div className="grid grid-cols-2 gap-4">
            <Input label="From Date" type="date" value={odFormData.fromDate} onChange={e => setOdFormData({...odFormData, fromDate: e.target.value})} required />
            <Input label="To Date" type="date" value={odFormData.toDate} onChange={e => setOdFormData({...odFormData, toDate: e.target.value})} required />
          </div>

          {odFormData.type === 'partial' && (
            <div className="grid grid-cols-2 gap-4">
              <Input label="From Time" type="time" value={odFormData.fromTime} onChange={e => setOdFormData({...odFormData, fromTime: e.target.value})} required />
              <Input label="To Time" type="time" value={odFormData.toTime} onChange={e => setOdFormData({...odFormData, toTime: e.target.value})} required />
            </div>
          )}

          <Input label="Location" placeholder="Client site, etc." value={odFormData.location} onChange={e => setOdFormData({...odFormData, location: e.target.value})} required />

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Reason</label>
            <textarea className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20" rows={3} value={odFormData.reason} onChange={e => setOdFormData({...odFormData, reason: e.target.value})} required />
          </div>
          <div className="flex gap-3 pt-2">
            <AnimatedButton type="button" variant="ghost" fullWidth onClick={() => setShowOdModal(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" variant="primary" fullWidth icon={Send}>Submit OD</AnimatedButton>
          </div>
        </form>
      </Modal>

      {/* Miss Punch Modal */}
      <Modal isOpen={showMissPunchModal} onClose={() => setShowMissPunchModal(false)} title="Miss Punch Request" size="md">
        <form onSubmit={handleMissPunchSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Date" type="date" value={mpFormData.date} onChange={e => setMpFormData({...mpFormData, date: e.target.value})} required />
            <Select label="Type" options={[
              {value: 'MISSING_IN', label: 'Missing Check-In'},
              {value: 'MISSING_OUT', label: 'Missing Check-Out'}
            ]} value={mpFormData.type} onChange={e => setMpFormData({...mpFormData, type: e.target.value})} required />
          </div>
          <Input label="Requested Time (HH:MM)" type="time" value={mpFormData.time} onChange={e => setMpFormData({...mpFormData, time: e.target.value})} required />
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Reason</label>
            <textarea className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20" rows={3} value={mpFormData.reason} onChange={e => setMpFormData({...mpFormData, reason: e.target.value})} required />
          </div>
          <div className="flex gap-3 pt-2">
            <AnimatedButton type="button" variant="ghost" fullWidth onClick={() => setShowMissPunchModal(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" variant="primary" fullWidth icon={Send}>Submit</AnimatedButton>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
};

export default LeaveManagement;
