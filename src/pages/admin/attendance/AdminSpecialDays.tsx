import React, { useEffect, useState } from 'react';
import { Plus, Save, Trash2, Edit2, Calendar, Ban, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { 
  SpecialDay, 
  getSpecialDays, 
  createSpecialDay, 
  updateSpecialDay, 
  cancelSpecialDay, 
  SpecialDayPayload 
} from '../../services/specialDayService';
import { organizationApi } from '../../services/organization.api';

export const AdminSpecialDays: React.FC = () => {
  const [specialDays, setSpecialDays] = useState<SpecialDay[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form State
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [eventName, setEventName] = useState('');
  const [date, setDate] = useState('');
  const [dayType, setDayType] = useState<'Sudden Holiday' | 'Sudden Cutoff'>('Sudden Holiday');
  const [applicability, setApplicability] = useState<'All Branches' | 'Selected Branches'>('All Branches');
  const [selectedBranchIds, setSelectedBranchIds] = useState<string[]>([]);
  const [expectedWorkingHours, setExpectedWorkingHours] = useState<string>('4.0');
  const [reason, setReason] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sdRes, branchRes] = await Promise.all([
        getSpecialDays(),
        organizationApi.getBranches()
      ]);
      setSpecialDays(sdRes || []);
      setBranches(branchRes?.data || branchRes || []);
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
    setDayType('Sudden Holiday');
    setApplicability('All Branches');
    setSelectedBranchIds([]);
    setExpectedWorkingHours('4.0');
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
    setApplicability(item.applicability);
    setSelectedBranchIds(item.selectedBranchIds || []);
    setExpectedWorkingHours(item.expectedWorkingHours ? item.expectedWorkingHours.toString() : '4.0');
    setReason(item.reason || '');
    setIsFormOpen(true);
    setError(null);
    setSuccess(null);
  };

  const handleBranchToggle = (branchId: string) => {
    setSelectedBranchIds(prev => 
      prev.includes(branchId) ? prev.filter(id => id !== branchId) : [...prev, branchId]
    );
  };

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
          expectedWorkingHours: dayType === 'Sudden Cutoff' ? parseFloat(expectedWorkingHours) : null
        });
        setSuccess('Configuration updated successfully.');
      } else {
        const payload: SpecialDayPayload = {
          eventName: eventName.trim(),
          date,
          dayType,
          applicability,
          selectedBranchIds: applicability === 'Selected Branches' ? selectedBranchIds : [],
          expectedWorkingHours: dayType === 'Sudden Cutoff' ? parseFloat(expectedWorkingHours) : null,
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
          <h2 className="text-xl font-bold text-neutral-900">Special Day Configurations</h2>
          <p className="text-sm text-neutral-500">
            Configure exceptional day declarations: Sudden Holidays or Sudden Cutoffs (Special Working Hours).
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
              {editingId ? 'Edit Special Day Configuration' : 'Create Special Day Configuration'}
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
                  placeholder="e.g. Cyclone Relief Holiday / Founder's Half Day"
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
                  <option value="Sudden Holiday">Sudden Holiday</option>
                  <option value="Sudden Cutoff">Sudden Cutoff (Special Working Hours)</option>
                </select>
                {editingId && <p className="text-xs text-neutral-400 mt-1">Day type cannot be changed on edit.</p>}
              </div>

              {dayType === 'Sudden Cutoff' && (
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium text-neutral-700">
                      Expected Working Hours *
                    </label>
                    <span className="text-xs text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
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

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">Applicability Scope *</label>
                <select
                  value={applicability}
                  onChange={(e) => setApplicability(e.target.value as any)}
                  disabled={Boolean(editingId)}
                  className="w-full h-10 px-3 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                >
                  <option value="All Branches">All Branches</option>
                  <option value="Selected Branches">Selected Branches</option>
                </select>
                {editingId && <p className="text-xs text-neutral-400 mt-1">Applicability scope cannot be changed on edit.</p>}
              </div>
            </div>

            {applicability === 'Selected Branches' && (
              <div className="border border-neutral-200 rounded-lg p-4 bg-neutral-50">
                <label className="block text-sm font-medium text-neutral-800 mb-2">
                  Select Applicable Branches *
                </label>
                {branches.length === 0 ? (
                  <p className="text-sm text-neutral-500">No branches found in your company.</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 max-h-48 overflow-y-auto p-1">
                    {branches.map((b) => {
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
        <h3 className="text-lg font-bold text-neutral-900 mb-4">Configured Special Days</h3>
        {isLoading ? (
          <p className="text-sm text-neutral-500 py-6 text-center">Loading configurations...</p>
        ) : specialDays.length === 0 ? (
          <div className="py-12 text-center text-neutral-500 space-y-2">
            <Calendar className="w-10 h-10 mx-auto text-neutral-400" />
            <p className="text-sm font-medium">No special day configurations declared yet.</p>
            <p className="text-xs text-neutral-400">Click 'New Configuration' above to declare a Sudden Holiday or Cutoff.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Event Name</th>
                  <th className="py-3 px-3">Day Type</th>
                  <th className="py-3 px-3">Applicability</th>
                  <th className="py-3 px-3">Expected Hours</th>
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
                      <td className="py-3 px-3">
                        <div className="font-medium text-neutral-800">{item.eventName}</div>
                        {item.reason && <div className="text-xs text-neutral-400 truncate max-w-xs">{item.reason}</div>}
                      </td>
                      <td className="py-3 px-3">
                        {item.dayType === 'Sudden Holiday' ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                            Sudden Holiday
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                            <Clock className="w-3 h-3" />
                            Sudden Cutoff
                          </span>
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
                        {item.dayType === 'Sudden Cutoff' && item.expectedWorkingHours != null ? (
                          <span className="font-mono font-medium text-neutral-800">
                            {item.expectedWorkingHours} hrs
                          </span>
                        ) : (
                          <span className="text-neutral-400">-</span>
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
