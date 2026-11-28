import React, { useEffect, useState } from 'react';
import { Plus, Save, Trash2, Edit2, Calendar, Ban, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../../components/ui';
import { 
  SpecialDay, 
  getSpecialDays, 
  createSpecialDay, 
  updateSpecialDay, 
  cancelSpecialDay, 
  SpecialDayPayload 
} from '../../../services/specialDayService';
import { organizationApi } from '../../../services/organization.api';
import { getShiftsV2, ShiftV2 } from '../../../services/shiftService';

export const AdminSpecialDays: React.FC = () => {
  const [specialDays, setSpecialDays] = useState<SpecialDay[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [shifts, setShifts] = useState<ShiftV2[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form State
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [eventName, setEventName] = useState('');
  const [date, setDate] = useState('');
  const [dayType, setDayType] = useState<'Sudden Holiday' | 'Sudden Shift Change' | 'Sudden Cutoff'>('Sudden Shift Change');
  
  // Scope State: Global - All Companies | Selected Companies | Single Company
  const [scopeType, setScopeType] = useState<'GLOBAL' | 'SELECTED_COMPANIES' | 'SINGLE_COMPANY'>('SINGLE_COMPANY');
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('');
  const [selectedCompanyIds, setSelectedCompanyIds] = useState<string[]>([]);

  const [applicability, setApplicability] = useState<'All Branches' | 'Selected Branches'>('All Branches');
  const [selectedBranchIds, setSelectedBranchIds] = useState<string[]>([]);
  
  // Shift timing fields
  const [selectedPresetShiftId, setSelectedPresetShiftId] = useState<string>('');
  const [startTime, setStartTime] = useState<string>('09:00');
  const [endTime, setEndTime] = useState<string>('18:00');
  const [isCrossMidnight, setIsCrossMidnight] = useState<boolean>(false);
  const [breakStartTime, setBreakStartTime] = useState<string>('');
  const [breakEndTime, setBreakEndTime] = useState<string>('');
  const [expectedWorkingHours, setExpectedWorkingHours] = useState<string>('8.0');

  const [reason, setReason] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sdRes, branchRes, shiftRes, compRes] = await Promise.all([
        getSpecialDays(),
        organizationApi.getBranches(),
        getShiftsV2(),
        organizationApi.getCompanies()
      ]);
      setSpecialDays(sdRes || []);
      setBranches(branchRes?.data || branchRes || []);
      setShifts(shiftRes || []);
      const comps = compRes?.data || compRes || [];
      setCompanies(comps);
      if (comps.length > 0 && !selectedCompanyId) {
        setSelectedCompanyId(comps[0].id || comps[0]._id || '');
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load special day configurations');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setEventName('');
    setDate('');
    setDayType('Sudden Shift Change');
    setScopeType('SINGLE_COMPANY');
    if (companies.length > 0) {
      setSelectedCompanyId(companies[0].id || companies[0]._id || '');
    }
    setSelectedCompanyIds([]);
    setApplicability('All Branches');
    setSelectedBranchIds([]);
    setSelectedPresetShiftId('');
    setStartTime('09:00');
    setEndTime('18:00');
    setIsCrossMidnight(false);
    setBreakStartTime('');
    setBreakEndTime('');
    setExpectedWorkingHours('8.0');
    setReason('');
    setIsFormOpen(false);
    setError(null);
    setSuccess(null);
  };

  const handleOpenCreate = () => {
    resetForm();
    setIsFormOpen(true);
  };

  const handleOpenEdit = (item: SpecialDay) => {
    setEditingId(item.id || item._id || item.specialDayId || null);
    setEventName(item.eventName);
    setDate(item.date);
    setDayType(item.dayType);
    setScopeType(item.scopeType || (item.companyId ? 'SINGLE_COMPANY' : 'GLOBAL'));
    setSelectedCompanyId(item.companyId || (item.companyIds && item.companyIds[0]) || '');
    setSelectedCompanyIds(item.companyIds || (item.companyId ? [item.companyId] : []));
    setApplicability(item.applicability);
    setSelectedBranchIds(item.selectedBranchIds || []);
    setSelectedPresetShiftId(item.shiftId || '');
    setStartTime(item.startTime || '09:00');
    setEndTime(item.endTime || '18:00');
    setIsCrossMidnight(Boolean(item.isCrossMidnight));
    setBreakStartTime(item.breakStartTime || '');
    setBreakEndTime(item.breakEndTime || '');
    setExpectedWorkingHours(item.expectedWorkingHours ? item.expectedWorkingHours.toString() : '8.0');
    setReason(item.reason || '');
    setIsFormOpen(true);
    setError(null);
    setSuccess(null);
  };

  const handleCompanyMultiToggle = (cid: string) => {
    setSelectedCompanyIds(prev => 
      prev.includes(cid) ? prev.filter(id => id !== cid) : [...prev, cid]
    );
  };

  const handlePresetShiftChange = (shiftId: string) => {
    setSelectedPresetShiftId(shiftId);
    if (!shiftId) return;
    const match = shifts.find(s => (s._id || s.shiftCode) === shiftId);
    if (match) {
      if (match.startTime) setStartTime(match.startTime.slice(0, 5));
      if (match.endTime) setEndTime(match.endTime.slice(0, 5));
      setIsCrossMidnight(Boolean(match.isCrossMidnight));
      if (match.breakStartTime) setBreakStartTime(match.breakStartTime.slice(0, 5));
      if (match.breakEndTime) setBreakEndTime(match.breakEndTime.slice(0, 5));
    }
  };

  const handleBranchToggle = (branchId: string) => {
    setSelectedBranchIds(prev => 
      prev.includes(branchId) ? prev.filter(id => id !== branchId) : [...prev, branchId]
    );
  };

  // Filter available branches based on scope
  const availableBranches = branches.filter(b => {
    if (scopeType === 'GLOBAL') return true;
    if (scopeType === 'SINGLE_COMPANY') return !selectedCompanyId || String(b.companyId) === String(selectedCompanyId);
    if (scopeType === 'SELECTED_COMPANIES') return selectedCompanyIds.length === 0 || selectedCompanyIds.includes(String(b.companyId));
    return true;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!eventName.trim()) {
      setError('Event Name is required.');
      return;
    }
    if (!date) {
      setError('Date is required.');
      return;
    }
    if (scopeType === 'SINGLE_COMPANY' && !selectedCompanyId) {
      setError('Please select a company for Single Company scope.');
      return;
    }
    if (scopeType === 'SELECTED_COMPANIES' && selectedCompanyIds.length === 0) {
      setError('Please select at least one company for Selected Companies scope.');
      return;
    }

    if (dayType === 'Sudden Shift Change') {
      if (!startTime || !endTime) {
        setError('Expected IN Time and Expected OUT Time are required for Sudden Shift Change.');
        return;
      }
    }
    if (dayType === 'Sudden Cutoff') {
      const hours = parseFloat(expectedWorkingHours);
      if (isNaN(hours) || hours <= 0 || hours > 24) {
        setError('Expected Working Hours must be between 0.5 and 24.0.');
        return;
      }
    }
    if (applicability === 'Selected Branches' && selectedBranchIds.length === 0) {
      setError('Please select at least one branch for Selected Branches applicability.');
      return;
    }

    setIsSaving(true);
    try {
      if (editingId) {
        await updateSpecialDay(editingId, {
          eventName: eventName.trim(),
          reason: reason.trim(),
          startTime: dayType === 'Sudden Shift Change' ? startTime : null,
          endTime: dayType === 'Sudden Shift Change' ? endTime : null,
          isCrossMidnight: dayType === 'Sudden Shift Change' ? isCrossMidnight : false,
          breakStartTime: dayType === 'Sudden Shift Change' ? breakStartTime || null : null,
          breakEndTime: dayType === 'Sudden Shift Change' ? breakEndTime || null : null,
          expectedWorkingHours: (dayType === 'Sudden Cutoff' || dayType === 'Sudden Shift Change') ? parseFloat(expectedWorkingHours) : null
        });
        setSuccess('Configuration updated successfully.');
      } else {
        const payload: SpecialDayPayload = {
          eventName: eventName.trim(),
          date,
          dayType,
          scopeType,
          companyId: scopeType === 'SINGLE_COMPANY' ? selectedCompanyId : undefined,
          companyIds: scopeType === 'SELECTED_COMPANIES' ? selectedCompanyIds : undefined,
          applicability,
          selectedBranchIds: applicability === 'Selected Branches' ? selectedBranchIds : [],
          shiftId: dayType === 'Sudden Shift Change' ? selectedPresetShiftId || null : null,
          startTime: dayType === 'Sudden Shift Change' ? startTime : null,
          endTime: dayType === 'Sudden Shift Change' ? endTime : null,
          isCrossMidnight: dayType === 'Sudden Shift Change' ? isCrossMidnight : false,
          breakStartTime: dayType === 'Sudden Shift Change' ? breakStartTime || null : null,
          breakEndTime: dayType === 'Sudden Shift Change' ? breakEndTime || null : null,
          expectedWorkingHours: (dayType === 'Sudden Cutoff' || dayType === 'Sudden Shift Change') ? parseFloat(expectedWorkingHours) : null,
          reason: reason.trim() || null
        };
        await createSpecialDay(payload);
        setSuccess('Special Day Configuration created successfully.');
      }
      await loadData();
      resetForm();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelConfig = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to cancel '${name}'? This cannot be undone.`)) {
      return;
    }
    try {
      await cancelSpecialDay(id);
      setSuccess(`'${name}' cancelled successfully.`);
      await loadData();
    } catch (err: any) {
      setError(err?.message || 'Failed to cancel configuration');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-neutral-900">Special Day & Shift Configurations</h2>
          <p className="text-sm text-neutral-500">
            Configure exceptional day declarations: Sudden Holiday, Sudden Shift Change (Revised Timings), or Sudden Cutoff.
          </p>
        </div>
        {!isFormOpen && (
          <AnimatedButton onClick={handleOpenCreate} icon={Plus}>
            New Configuration
          </AnimatedButton>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center gap-2 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-lg bg-green-50 border border-green-200 text-green-700 flex items-center gap-2 text-sm">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* Form Card */}
      {isFormOpen && (
        <GlassCard className="p-6 border border-indigo-200 shadow-md">
          <div className="flex justify-between items-center mb-6 border-b pb-3">
            <h3 className="text-lg font-bold text-neutral-800">
              {editingId ? 'Edit Special Configuration' : 'Create Special Configuration'}
            </h3>
            <button
              onClick={resetForm}
              className="text-sm text-neutral-500 hover:text-neutral-700"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Event Name *</label>
                <Input
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="e.g. Town Hall Shift / Emergency Weather Holiday"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Date *</label>
                <Input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  disabled={Boolean(editingId)}
                  required
                />
                {editingId && <p className="text-xs text-neutral-400 mt-1">Date cannot be changed once created.</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Day Type *</label>
                <select
                  value={dayType}
                  onChange={(e) => setDayType(e.target.value as any)}
                  disabled={Boolean(editingId)}
                  className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="Sudden Shift Change">Sudden Shift Change (Revised Timings)</option>
                  <option value="Sudden Holiday">Sudden Holiday</option>
                  <option value="Sudden Cutoff">Sudden Cutoff (Hours Shortfall Exception)</option>
                </select>
                {editingId && <p className="text-xs text-neutral-400 mt-1">Day type cannot be changed on edit.</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Applicability Scope *</label>
                <select
                  value={scopeType}
                  onChange={(e) => {
                    const newScope = e.target.value as 'GLOBAL' | 'SELECTED_COMPANIES' | 'SINGLE_COMPANY';
                    setScopeType(newScope);
                    setSelectedBranchIds([]);
                  }}
                  disabled={Boolean(editingId)}
                  className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="SINGLE_COMPANY">Single Company</option>
                  <option value="SELECTED_COMPANIES">Selected Companies</option>
                  <option value="GLOBAL">Global – All Companies</option>
                </select>
                {editingId && <p className="text-xs text-neutral-400 mt-1">Scope cannot be changed on edit.</p>}
              </div>

              {scopeType === 'SINGLE_COMPANY' && (
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-1">Company *</label>
                  <select
                    value={selectedCompanyId}
                    onChange={(e) => {
                      setSelectedCompanyId(e.target.value);
                      setSelectedBranchIds([]);
                    }}
                    disabled={Boolean(editingId)}
                    className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    <option value="">-- Select Company --</option>
                    {companies.map((c) => {
                      const cId = c.id || c._id;
                      return (
                        <option key={cId} value={cId}>
                          {c.name || c.companyName || cId}
                        </option>
                      );
                    })}
                  </select>
                </div>
              )}

              {scopeType === 'GLOBAL' && (
                <div className="flex items-center">
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-xs text-purple-800">
                    <span className="font-semibold block">Global Scope Event</span>
                    Applies across all current and future companies in the system.
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Branch Applicability *</label>
                <select
                  value={applicability}
                  onChange={(e) => setApplicability(e.target.value as any)}
                  disabled={Boolean(editingId)}
                  className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="All Branches">All Branches</option>
                  <option value="Selected Branches">Selected Branches</option>
                </select>
                {editingId && <p className="text-xs text-neutral-400 mt-1">Branch applicability cannot be changed on edit.</p>}
              </div>
            </div>

            {/* Selected Companies multi-select */}
            {scopeType === 'SELECTED_COMPANIES' && (
              <div className="border border-indigo-200 rounded-lg p-4 bg-indigo-50/30">
                <label className="block text-sm font-medium text-neutral-800 mb-2">
                  Select Applicable Companies *
                </label>
                {companies.length === 0 ? (
                  <p className="text-sm text-neutral-500">No companies found.</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-40 overflow-y-auto p-1">
                    {companies.map((c) => {
                      const cId = c.id || c._id;
                      const isChecked = selectedCompanyIds.includes(cId);
                      return (
                        <label
                          key={cId}
                          className={`flex items-center gap-2 p-2 rounded border cursor-pointer text-sm transition-colors ${
                            isChecked
                              ? 'bg-indigo-50 border-indigo-300 text-indigo-900 font-medium'
                              : 'bg-white border-neutral-200 text-neutral-700 hover:bg-neutral-100'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => handleCompanyMultiToggle(cId)}
                            disabled={Boolean(editingId)}
                            className="rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                          />
                          <span>{c.name || c.companyName || cId}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
                {selectedCompanyIds.length > 0 && (
                  <p className="text-xs text-indigo-700 mt-2 font-medium">
                    {selectedCompanyIds.length} company(s) selected
                  </p>
                )}
              </div>
            )}

            {/* Shift Timings for Sudden Shift Change */}
            {dayType === 'Sudden Shift Change' && (
              <div className="border border-indigo-200 rounded-lg p-5 bg-indigo-50/40 space-y-4">
                <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-indigo-100 pb-3">
                  <div>
                    <h4 className="text-sm font-bold text-indigo-950 flex items-center gap-2">
                      <Clock className="w-4 h-4 text-indigo-600" />
                      Special Shift Timings for Date
                    </h4>
                    <p className="text-xs text-indigo-700">
                      Attendance calculations (Late IN, Early OUT, Duration) will evaluate against these exact shift times.
                    </p>
                  </div>
                  <div className="text-xs font-medium text-neutral-600 bg-white px-2.5 py-1 rounded border border-neutral-200">
                    Normal Assigned Shift: 09:00 - 18:00 (Reference)
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-1">
                      Predefined Shift (Optional Preset)
                    </label>
                    <select
                      value={selectedPresetShiftId}
                      onChange={(e) => handlePresetShiftChange(e.target.value)}
                      className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-sm"
                    >
                      <option value="">-- Custom Timings --</option>
                      {shifts.map(s => (
                        <option key={s._id || s.shiftCode} value={s._id || s.shiftCode}>
                          {s.name} ({s.startTime} - {s.endTime})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-1">
                      Expected IN Time *
                    </label>
                    <Input
                      type="time"
                      value={startTime}
                      onChange={(e) => setStartTime(e.target.value)}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-1">
                      Expected OUT Time *
                    </label>
                    <Input
                      type="time"
                      value={endTime}
                      onChange={(e) => setEndTime(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-1">
                      Break Start (Optional)
                    </label>
                    <Input
                      type="time"
                      value={breakStartTime}
                      onChange={(e) => setBreakStartTime(e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-1">
                      Break End (Optional)
                    </label>
                    <Input
                      type="time"
                      value={breakEndTime}
                      onChange={(e) => setBreakEndTime(e.target.value)}
                    />
                  </div>

                  <div className="flex items-center gap-2 pt-6">
                    <input
                      type="checkbox"
                      id="isCrossMidnight"
                      checked={isCrossMidnight}
                      onChange={(e) => setIsCrossMidnight(e.target.checked)}
                      className="rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                    />
                    <label htmlFor="isCrossMidnight" className="text-xs font-medium text-neutral-700 cursor-pointer">
                      Overnight Shift (Ends Next Day)
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Sudden Cutoff hours */}
            {dayType === 'Sudden Cutoff' && (
              <div className="border border-amber-200 rounded-lg p-4 bg-amber-50/40">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-neutral-700">
                    Expected Working Hours *
                  </label>
                  <span className="text-xs text-amber-700 bg-amber-100 px-2 py-0.5 rounded font-medium">
                    Normal Shift: 8.0 hrs
                  </span>
                </div>
                <Input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="24.0"
                  value={expectedWorkingHours}
                  onChange={(e) => setExpectedWorkingHours(e.target.value)}
                  placeholder="e.g. 4.0"
                  required
                />
                <p className="text-xs text-neutral-500 mt-1">
                  Employees completing this duration will be marked Present without working-hour shortfall.
                </p>
              </div>
            )}

            {applicability === 'Selected Branches' && (
              <div className="border border-neutral-200 rounded-lg p-4 bg-neutral-50">
                <label className="block text-sm font-medium text-neutral-800 mb-2">
                  Select Applicable Branches *
                </label>
                {availableBranches.length === 0 ? (
                  <p className="text-sm text-neutral-500">No branches found for the selected scope.</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-48 overflow-y-auto p-1">
                    {availableBranches.map((b) => {
                      const bId = b._id || b.id;
                      const isChecked = selectedBranchIds.includes(bId);
                      return (
                        <label
                          key={bId}
                          className={`flex items-center gap-2 p-2 rounded border cursor-pointer text-sm transition-colors ${
                            isChecked
                              ? 'bg-indigo-50 border-indigo-300 text-indigo-900 font-medium'
                              : 'bg-white border-neutral-200 text-neutral-700 hover:bg-neutral-100'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => handleBranchToggle(bId)}
                            disabled={Boolean(editingId)}
                            className="rounded text-indigo-600 focus:ring-indigo-500 h-4 w-4"
                          />
                          <span>{b.name || b.code || bId}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
                {selectedBranchIds.length > 0 && (
                  <p className="text-xs text-indigo-700 mt-2 font-medium">
                    {selectedBranchIds.length} branch(es) selected
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Reason / Description</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={2}
                placeholder="Reason or notes regarding this special declaration..."
                className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-neutral-300 rounded-md text-sm font-medium text-neutral-700 hover:bg-neutral-50"
              >
                Cancel
              </button>
              <AnimatedButton type="submit" disabled={isSaving} icon={Save}>
                {isSaving ? 'Saving...' : editingId ? 'Update Configuration' : 'Save Configuration'}
              </AnimatedButton>
            </div>
          </form>
        </GlassCard>
      )}

      {/* Listing Card */}
      <GlassCard className="p-6">
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Configured Special Days & Shifts</h3>
        {isLoading ? (
          <p className="text-sm text-neutral-500 py-6 text-center">Loading configurations...</p>
        ) : specialDays.length === 0 ? (
          <div className="py-12 text-center text-neutral-500 space-y-2">
            <Calendar className="w-10 h-10 mx-auto text-neutral-400" />
            <p className="text-sm font-medium">No special day configurations declared yet.</p>
            <p className="text-xs text-neutral-400">Click 'New Configuration' above to declare a Sudden Shift Change or Sudden Holiday.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Scope / Company</th>
                  <th className="py-3 px-3">Event Name</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Shift / Timings</th>
                  <th className="py-3 px-3">Applicability</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 text-sm">
                {specialDays.map((item) => {
                  const itemId = item.id || item._id || item.specialDayId || '';
                  const isActive = item.status === 'Active';
                  return (
                    <tr key={itemId} className={`hover:bg-neutral-50/50 ${!isActive ? 'opacity-60 bg-neutral-50/30' : ''}`}>
                      <td className="py-3 px-3 font-semibold text-neutral-900 whitespace-nowrap">
                        {item.date}
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        {item.scopeType === 'GLOBAL' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200">
                            Global (All)
                          </span>
                        ) : item.scopeType === 'SELECTED_COMPANIES' ? (
                          <div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                              Selected ({item.companyIds?.length || 0})
                            </span>
                            {item.companyNames && item.companyNames.length > 0 && (
                              <div className="text-[11px] text-neutral-500 truncate max-w-[140px]" title={item.companyNames.join(', ')}>
                                {item.companyNames.join(', ')}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div>
                            <span className="text-xs font-medium text-neutral-800">
                              {item.companyNames && item.companyNames[0] ? item.companyNames[0] : (item.companyId || 'Single Company')}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-medium text-neutral-800">{item.eventName}</div>
                        {item.reason && <div className="text-xs text-neutral-400 truncate max-w-xs">{item.reason}</div>}
                      </td>
                      <td className="py-3 px-3">
                        {item.dayType === 'Sudden Holiday' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                            Sudden Holiday
                          </span>
                        ) : item.dayType === 'Sudden Shift Change' ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
                            <Clock className="w-3 h-3" />
                            Special Shift
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                            <Clock className="w-3 h-3" />
                            Sudden Cutoff
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        {item.dayType === 'Sudden Shift Change' && item.startTime && item.endTime ? (
                          <div className="text-xs space-y-0.5">
                            <span className="font-mono font-medium text-neutral-800">
                              {item.startTime} - {item.endTime}
                            </span>
                            {item.isCrossMidnight && (
                              <span className="ml-1 text-[10px] text-purple-700 bg-purple-50 px-1 py-0.2 rounded border border-purple-200">
                                Overnight
                              </span>
                            )}
                            <div className="text-neutral-500 text-[11px]">
                              {item.expectedWorkingHours ? `${item.expectedWorkingHours}h expected` : ''}
                            </div>
                          </div>
                        ) : item.dayType === 'Sudden Cutoff' && item.expectedWorkingHours != null ? (
                          <span className="font-mono font-medium text-neutral-800 text-xs">
                            {item.expectedWorkingHours} hrs cutoff
                          </span>
                        ) : (
                          <span className="text-neutral-400 text-xs">Full Holiday</span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        {item.applicability === 'All Branches' ? (
                          <span className="text-xs font-medium text-neutral-600">All Branches</span>
                        ) : (
                          <div>
                            <span className="text-xs font-semibold text-indigo-700">Selected Branches</span>
                            <div className="text-xs text-neutral-400 truncate max-w-xs">
                              {item.selectedBranchNames && item.selectedBranchNames.length > 0
                                ? item.selectedBranchNames.join(', ')
                                : `${item.selectedBranchIds?.length || 0} branches`}
                            </div>
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        {isActive ? (
                          <StatusBadge status="success" label="Active" />
                        ) : (
                          <StatusBadge status="neutral" label="Cancelled" />
                        )}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {isActive && (
                            <>
                              <button
                                onClick={() => handleOpenEdit(item)}
                                className="p-1 rounded text-neutral-500 hover:text-indigo-600 hover:bg-neutral-100 transition-colors"
                                title="Edit"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleCancelConfig(itemId, item.eventName)}
                                className="p-1 rounded text-neutral-500 hover:text-red-600 hover:bg-neutral-100 transition-colors"
                                title="Cancel Configuration"
                              >
                                <Ban className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          {!isActive && (
                            <span className="text-xs text-neutral-400 italic">Cancelled</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
};

export default AdminSpecialDays;
