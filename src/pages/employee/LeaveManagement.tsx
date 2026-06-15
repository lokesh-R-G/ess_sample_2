import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar as CalendarIcon, MapPin, Plus, Clock, CheckCircle, XCircle, AlertCircle, Send } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input, Select } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { DonutChart } from '../../components/charts';
import { createLeaveRequest, getLeaveData, LeaveApplication, LeaveBalanceItem } from '../../services/leaveService';

export const LeaveManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'leave' | 'od' | 'history'>('leave');
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyType, setApplyType] = useState<'leave' | 'od'>('leave');
  const [formData, setFormData] = useState({ leaveType: '', fromDate: '', toDate: '', reason: '', odLocation: '' });
  const [leaveBalance, setLeaveBalance] = useState<Record<string, LeaveBalanceItem>>({});
  const [leaveApplications, setLeaveApplications] = useState<LeaveApplication[]>([]);
  const [leaveAnalysisData, setLeaveAnalysisData] = useState<number[]>([0, 0, 0]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadLeaveData = async () => {
      try {
        setIsLoading(true);
        const response = await getLeaveData();
        setLeaveBalance(response.leaveBalance ?? {});
        setLeaveApplications(response.requests ?? []);
        setLeaveAnalysisData(response.leaveAnalysisData ?? [0, 0, 0]);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Unable to load leave data');
      } finally {
        setIsLoading(false);
      }
    };

    loadLeaveData();
  }, []);


  const leaveTypes = [
    { value: 'annual', label: 'Annual Leave' },
    { value: 'sick', label: 'Sick Leave' },
    { value: 'casual', label: 'Casual Leave' },
    { value: 'earned', label: 'Earned Leave' },
    { value: 'compoff', label: 'Comp Off' },
  ];

  const statusColors: Record<string, 'success' | 'warning' | 'error'> = {
    approved: 'success',
    pending: 'warning',
    rejected: 'error',
  };

  const handleApply = (type: 'leave' | 'od') => { setApplyType(type); setShowApplyModal(true); };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createLeaveRequest({
        requestType: applyType,
        leaveType: formData.leaveType,
        fromDate: formData.fromDate,
        toDate: formData.toDate,
        reason: formData.reason,
        odLocation: formData.odLocation,
      });
      const response = await getLeaveData();
      setLeaveBalance(response.leaveBalance ?? {});
      setLeaveApplications(response.requests ?? []);
      setLeaveAnalysisData(response.leaveAnalysisData ?? [0, 0, 0]);
      setShowApplyModal(false);
      setFormData({ leaveType: '', fromDate: '', toDate: '', reason: '', odLocation: '' });
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Unable to submit leave request');
    }

  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {error ? <GlassCard className="p-4 border border-red-200 bg-red-50 text-red-700">{error}</GlassCard> : null}
        {isLoading ? <GlassCard className="p-4 text-sm text-neutral-500">Loading leave data...</GlassCard> : null}


        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {Object.entries(leaveBalance).map(([key, value], index) => (
                <motion.div key={key} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: index * 0.1 }} whileHover={{ scale: 1.02 }}>
                  <p className="text-xs text-neutral-500 capitalize mb-2">{key.replace(/([A-Z])/g, ' $1')}</p>
                  <div className="flex items-end gap-1"><span className="text-2xl font-bold text-neutral-900">{value.balance}</span><span className="text-sm text-neutral-500 mb-0.5">/ {value.total}</span></div>
                  <div className="mt-2 h-1.5 rounded-full bg-neutral-200 overflow-hidden"><motion.div className="h-full bg-primary-500 rounded-full" initial={{ width: 0 }} animate={{ width: `${(value.balance / value.total) * 100}%` }} transition={{ duration: 0.8, delay: 0.3 }} /></div>

                </motion.div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
        <motion.div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2">
            {[
              { id: 'leave', label: 'Leave Requests', icon: CalendarIcon },
              { id: 'od', label: 'OD Requests', icon: MapPin },
              { id: 'history', label: 'History', icon: Clock },
            ].map((tab) => (
              <motion.button key={tab.id} onClick={() => setActiveTab(tab.id as typeof activeTab)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id ? 'bg-primary-50 text-primary-600 border border-primary-300' : 'text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 border border-transparent'}`} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </motion.button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <AnimatedButton variant="primary" size="sm" icon={Plus} onClick={() => handleApply('leave')}>Apply Leave</AnimatedButton>
            <AnimatedButton variant="secondary" size="sm" icon={Plus} onClick={() => handleApply('od')}>Apply OD</AnimatedButton>
          </div>
        </motion.div>
        <AnimatePresence mode="wait">
          {activeTab === 'leave' && (
            <motion.div key="leave" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave Applications</h3>
                <div className="space-y-3">
                  {leaveApplications.filter((app) => app.requestType !== 'od').map((application, index) => (
                    <motion.div key={application._id ?? application.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-neutral-50 border border-neutral-200 hover:border-primary-300 transition-colors gap-4" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}>

                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${application.status === 'approved' ? 'bg-emerald-100' : application.status === 'pending' ? 'bg-amber-100' : 'bg-red-100'}`}>
                          {application.status === 'approved' ? <CheckCircle className="w-5 h-5 text-emerald-600" /> : application.status === 'pending' ? <AlertCircle className="w-5 h-5 text-amber-600" /> : <XCircle className="w-5 h-5 text-red-600" />}
                        </div>
                        <div>

                          <div className="flex items-center gap-2"><p className="text-sm font-medium text-neutral-900">{application.leaveType ?? 'Leave'}</p><StatusBadge status={statusColors[application.status]} label={application.status} size="sm" /></div>
                          <p className="text-xs text-neutral-500 mt-1">{application.fromDate} - {application.toDate}</p>
                        </div>
                      </div>
                      <div className="text-sm text-neutral-600">{application.appliedOn}</div>
                    </motion.div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          )}
          {activeTab === 'od' && (
            <motion.div key="od" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">OD Applications</h3>
                <div className="space-y-3">
                  {leaveApplications.filter((app) => app.requestType === 'od').map((application, index) => (
                    <motion.div key={application._id ?? application.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-neutral-50 border border-neutral-200 gap-4" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.1 }}>
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-xl bg-purple-100"><MapPin className="w-5 h-5 text-purple-600" /></div>
                        <div>
                          <p className="text-sm font-medium text-neutral-900">{application.odLocation ?? application.reason ?? 'OD Request'}</p>                          <p className="text-xs text-neutral-500">{application.fromDate}</p>
                        </div>
                      </div>
                      <StatusBadge status={statusColors[application.status]} label={application.status} size="sm" />
                    </motion.div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          )}
          {activeTab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <GlassCard className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave & OD History</h3>
                <div className="space-y-3">
                  {leaveApplications.map((application, index) => (
                    <motion.div key={application._id ?? application.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-neutral-50 border border-neutral-200" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: index * 0.05 }}>
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${application.requestType === 'od' ? 'bg-purple-100' : 'bg-primary-100'}`}>
                          {application.requestType === 'od' ? <MapPin className="w-5 h-5 text-purple-600" /> : <CalendarIcon className="w-5 h-5 text-primary-600" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-neutral-900">{application.requestType === 'od' ? 'OD' : application.leaveType || 'Leave'}</p>

                          <p className="text-xs text-neutral-500">{application.reason}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mt-2 sm:mt-0">
                        <StatusBadge status={statusColors[application.status]} label={application.status} size="sm" />
                        <span className="text-xs text-neutral-500">{application.fromDate}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          )}
        </AnimatePresence>
        <motion.div className="grid grid-cols-1 lg:grid-cols-2 gap-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="p-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Leave Analysis</h3>
            <DonutChart labels={['Leave', 'OD', 'Pending']} series={leaveAnalysisData} height={220} />
          </GlassCard>
        </motion.div>
      </div>

      <Modal isOpen={showApplyModal} onClose={() => setShowApplyModal(false)} title={`Apply ${applyType === 'leave' ? 'Leave' : 'OD'}`} size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          {applyType === 'leave' && <Select label="Leave Type" options={leaveTypes} value={formData.leaveType} onChange={(e) => setFormData({ ...formData, leaveType: e.target.value })} placeholder="Select leave type" />}
          {applyType === 'od' && <Input label="Location" placeholder="Enter OD location" value={formData.odLocation} onChange={(e) => setFormData({ ...formData, odLocation: e.target.value })} />}
          <div className="grid grid-cols-2 gap-4">
            <Input label="From Date" type="date" value={formData.fromDate} onChange={(e) => setFormData({ ...formData, fromDate: e.target.value })} />
            <Input label="To Date" type="date" value={formData.toDate} onChange={(e) => setFormData({ ...formData, toDate: e.target.value })} />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">Reason</label>
            <textarea className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-300 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all resize-none" rows={3} placeholder="Enter reason for leave/OD" value={formData.reason} onChange={(e) => setFormData({ ...formData, reason: e.target.value })} />
          </div>
          <div className="flex gap-3 pt-2">
            <AnimatedButton type="button" variant="ghost" fullWidth onClick={() => setShowApplyModal(false)}>Cancel</AnimatedButton>
            <AnimatedButton type="submit" variant="primary" fullWidth icon={Send}>Submit</AnimatedButton>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
};


export default LeaveManagement;

