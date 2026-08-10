import React, { useEffect, useState } from 'react';
import { Plus, Save, Trash2, Edit2, Calendar } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { 
  HolidayCalendar, HolidayDate, 
  getHolidayCalendars, createHolidayCalendar, updateHolidayCalendar, deleteHolidayCalendar,
  getHolidayDates, createHolidayDate, updateHolidayDate, deleteHolidayDate 
} from '../../services/holidayCalendarService';

import { organizationApi } from '../../services/organization.api';

export const AdminHolidays: React.FC = () => {
  const [calendars, setCalendars] = useState<HolidayCalendar[]>([]);
  const [branches, setBranches] = useState<any[]>([]);
  const [selectedCalendar, setSelectedCalendar] = useState<HolidayCalendar | null>(null);
  const [editingCalendar, setEditingCalendar] = useState<HolidayCalendar | null>(null);
  
  const [dates, setDates] = useState<HolidayDate[]>([]);
  const [editingDate, setEditingDate] = useState<HolidayDate | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [calHistoryModalOpen, setCalHistoryModalOpen] = useState(false);
  const [dateHistoryModalOpen, setDateHistoryModalOpen] = useState(false);
  const [selectedCalHistory, setSelectedCalHistory] = useState<HolidayCalendar[]>([]);
  const [selectedDateHistory, setSelectedDateHistory] = useState<HolidayDate[]>([]);

  useEffect(() => {
    loadCalendars();
    loadBranches();
  }, []);

  const loadCalendars = async () => {
    try {
      const data = await getHolidayCalendars();
      setCalendars(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadBranches = async () => {
    try {
      const data = await organizationApi.getBranches();
      setBranches(data?.data || data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const loadDates = async (calendarId: string) => {
    try {
      const data = await getHolidayDates(calendarId);
      setDates(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectCalendar = (c: HolidayCalendar) => {
    setSelectedCalendar(c);
    const calId = c.id || c._id;
    if (calId) loadDates(calId);
  };

  const handleOpenCalHistory = async (code: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v2/holiday/holiday-calendar/history/${code}`, {
          headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
          const data = await res.json();
          setSelectedCalHistory(data || []);
          setCalHistoryModalOpen(true);
      } else {
          alert("Could not fetch history");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenDateHistory = async (calendarId: string, code: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/v2/holiday/holiday-calendar/${calendarId}/dates/history/${code}`, {
          headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
          const data = await res.json();
          setSelectedDateHistory(data || []);
          setDateHistoryModalOpen(true);
      } else {
          alert("Could not fetch history");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Calendar CRUD
  const handleSaveCalendar = async () => {
    if (!editingCalendar) return;
    try {
      setIsSaving(true);
      const calId = editingCalendar.id || editingCalendar._id;
      if (calId) {
        await updateHolidayCalendar(calId, editingCalendar);
      } else {
        if (!editingCalendar.holidayCalendarCode) {
            alert("Code is required");
            setIsSaving(false);
            return;
        }
        await createHolidayCalendar(editingCalendar);
      }
      setEditingCalendar(null);
      await loadCalendars();
    } catch (err: any) {
      alert(err.message || "Failed to save calendar");
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  // Date CRUD
  const handleSaveDate = async () => {
    const calId = selectedCalendar?.id || selectedCalendar?._id;
    if (!editingDate || !calId) return;
    try {
      setIsSaving(true);
      const dateId = editingDate.id || editingDate._id;
      if (dateId) {
        await updateHolidayDate(calId, dateId, editingDate);
      } else {
        if (!editingDate.holidayCode) {
            alert("Holiday Code is required");
            setIsSaving(false);
            return;
        }
        await createHolidayDate(calId, editingDate);
      }
      setEditingDate(null);
      await loadDates(calId);
    } catch (err: any) {
      alert(err.message || "Failed to save date");
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Holiday Calendars</h1>
          <p className="text-sm text-neutral-500">Manage multiple holiday calendars and assign them to branches.</p>
        </div>
        {!editingCalendar && !selectedCalendar && (
          <AnimatedButton icon={Plus} onClick={() => setEditingCalendar({ holidayCalendarCode: '', name: '', year: new Date().getFullYear() })}>New Calendar</AnimatedButton>
        )}
      </div>

      {editingCalendar && (
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4">{(editingCalendar.id || editingCalendar._id) ? 'Edit Calendar' : 'Create Calendar'}</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <Input label="Calendar Code" value={editingCalendar.holidayCalendarCode || ''} onChange={e => setEditingCalendar({...editingCalendar, holidayCalendarCode: e.target.value})} disabled={!!(editingCalendar.id || editingCalendar._id)} required />
            <Input label="Name" value={editingCalendar.name} onChange={e => setEditingCalendar({...editingCalendar, name: e.target.value})} />
            <Input type="number" label="Year" value={editingCalendar.year} onChange={e => setEditingCalendar({...editingCalendar, year: parseInt(e.target.value)})} />
            <Input label="Description" value={editingCalendar.description || ''} onChange={e => setEditingCalendar({...editingCalendar, description: e.target.value})} />
            <Input type="date" label="Effective From" value={editingCalendar.effectiveFrom ? editingCalendar.effectiveFrom.split('T')[0] : ''} onChange={e => setEditingCalendar({...editingCalendar, effectiveFrom: e.target.value})} />
            <Input type="date" label="Effective To" value={editingCalendar.effectiveTo ? editingCalendar.effectiveTo.split('T')[0] : ''} onChange={e => setEditingCalendar({...editingCalendar, effectiveTo: e.target.value})} />

            
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Branch</label>
              <select className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg" value={editingCalendar.branchId || ''} onChange={e => setEditingCalendar({...editingCalendar, branchId: e.target.value})}>
                <option value="">Global (All Branches)</option>
                {branches.map(b => (
                  <option key={b._id || b.id} value={b._id || b.id}>{b.code ? `${b.code} - ${b.name}` : b.name}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <AnimatedButton variant="secondary" onClick={() => setEditingCalendar(null)}>Cancel</AnimatedButton>
            <AnimatedButton icon={Save} loading={isSaving} onClick={handleSaveCalendar}>Save Calendar</AnimatedButton>
          </div>
        </GlassCard>
      )}

      {!selectedCalendar && !editingCalendar && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {calendars.filter(c => c.isCurrent !== false).map(c => (
            <GlassCard key={c.id || c._id} className="p-4 cursor-pointer hover:border-primary-500 transition-colors" onClick={() => handleSelectCalendar(c)}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm bg-neutral-100 px-2 py-0.5 rounded">{c.holidayCalendarCode}</span>
                    <StatusBadge status="Active" label={`v${c.version || 1}`} />
                  </div>
                  <h3 className="font-semibold text-lg">{c.name}</h3>
                </div>
                <StatusBadge status={c.status === 'Active' ? 'success' : 'neutral'} label={c.status || 'Active'} />
              </div>
              <p className="text-sm text-neutral-500 mb-2">{c.description || 'No description'}</p>
              <div className="flex flex-col gap-1 mb-4">
                <div className="text-xs bg-neutral-100 p-1 rounded font-mono inline-block w-max">Branch: {c.branchCode ? `${c.branchCode} - ${c.branchName}` : (c.branchName || c.branchId || 'Global')}</div>
                <div className="text-xs text-neutral-500">
                  Effective: {c.effectiveFrom ? new Date(c.effectiveFrom).toLocaleDateString() : 'N/A'} - {c.effectiveTo ? new Date(c.effectiveTo).toLocaleDateString() : 'N/A'}
                </div>
                <div className="text-xs font-semibold text-primary-600 mt-1">Holidays: {c.holidayCount || 0}</div>
              </div>
              <div className="flex justify-end gap-2" onClick={e => e.stopPropagation()}>
                <AnimatedButton variant="secondary" size="sm" onClick={() => handleOpenCalHistory(c.holidayCalendarCode || '')}>History</AnimatedButton>
                <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={() => setEditingCalendar(c)}>Edit</AnimatedButton>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {selectedCalendar && (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <AnimatedButton variant="secondary" onClick={() => setSelectedCalendar(null)}>← Back to Calendars</AnimatedButton>
            <h2 className="text-xl font-bold">{selectedCalendar.name} ({selectedCalendar.year})</h2>
          </div>

          <GlassCard className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold flex items-center gap-2"><Calendar className="w-5 h-5 text-blue-500"/> Holiday Dates</h3>
              {!editingDate && (
                <AnimatedButton size="sm" icon={Plus} onClick={() => setEditingDate({ calendarId: selectedCalendar.id || selectedCalendar._id!, holidayCode: '', holidayName: '', holidayDate: '', holidayType: 'Mandatory', isRecurring: false, remarks: '' })}>Add Date</AnimatedButton>
              )}
            </div>

            {editingDate && (
              <div className="bg-neutral-50 p-4 rounded-lg border mb-6">
                <div className="grid grid-cols-4 gap-4 mb-4">
                  <Input label="Holiday Code" value={editingDate.holidayCode || ''} onChange={e => setEditingDate({...editingDate, holidayCode: e.target.value})} disabled={!!(editingDate.id || editingDate._id)} required />
                  <Input type="date" label="Date" value={editingDate.holidayDate.split('T')[0]} onChange={e => setEditingDate({...editingDate, holidayDate: e.target.value})} />
                  <Input label="Holiday Name" value={editingDate.holidayName} onChange={e => setEditingDate({...editingDate, holidayName: e.target.value})} />
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-1">Type</label>
                    <select className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg" value={editingDate.holidayType} onChange={e => setEditingDate({...editingDate, holidayType: e.target.value})}>
                      <option value="Mandatory">Mandatory</option>
                      <option value="Restricted">Restricted</option>
                      <option value="Optional">Optional</option>
                      <option value="National">National</option>
                      <option value="Festival">Festival</option>
                      <option value="Branch">Branch</option>
                    </select>
                  </div>
                  <Input label="Remarks" value={editingDate.remarks || ''} onChange={e => setEditingDate({...editingDate, remarks: e.target.value})} />
                  <div className="flex items-center gap-2 mt-6">
                    <input type="checkbox" id="recurring" checked={editingDate.isRecurring || false} onChange={e => setEditingDate({...editingDate, isRecurring: e.target.checked})} />
                    <label htmlFor="recurring" className="text-sm font-medium text-neutral-700">Recurring Yearly</label>
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <AnimatedButton variant="secondary" size="sm" onClick={() => setEditingDate(null)}>Cancel</AnimatedButton>
                  <AnimatedButton icon={Save} size="sm" loading={isSaving} onClick={handleSaveDate}>Save Date</AnimatedButton>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {dates.filter(d => d.isCurrent !== false).map(d => (
                <div key={d.id || d._id} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-xs bg-neutral-100 px-2 py-0.5 rounded">{d.holidayCode}</span>
                    <StatusBadge status="Active" label={`v${d.version || 1}`} />
                    <div className="bg-primary-50 text-primary-700 px-3 py-1 rounded font-medium">{new Date(d.holidayDate).toLocaleDateString()}</div>
                    <div className="font-medium text-neutral-900">{d.holidayName}</div>
                    <StatusBadge status={d.holidayType === 'Mandatory' || d.holidayType === 'National' ? 'error' : 'info'} label={d.holidayType} />
                    {d.isRecurring && <StatusBadge status="warning" label="Recurring" />}
                  </div>
                  <div className="flex gap-2">
                    <AnimatedButton variant="secondary" size="sm" onClick={() => handleOpenDateHistory(selectedCalendar.id || selectedCalendar._id!, d.holidayCode || '')}>History</AnimatedButton>
                    <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={() => setEditingDate(d)}>Edit</AnimatedButton>
                    <AnimatedButton variant="danger" size="sm" icon={Trash2} onClick={async () => {
                      if(confirm('Delete holiday?')) {
                        const calId = selectedCalendar.id || selectedCalendar._id;
                        const dId = d.id || d._id;
                        if(calId && dId) {
                          await deleteHolidayDate(calId, dId);
                          loadDates(calId);
                        }
                      }
                    }}>Delete</AnimatedButton>
                  </div>
                </div>
              ))}
              {dates.length === 0 && <p className="text-neutral-500 italic text-center py-4">No holidays defined.</p>}
            </div>
          </GlassCard>
        </div>
      )}

      {calHistoryModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="px-6 py-4 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">Calendar Version History</h3>
              <button onClick={() => setCalHistoryModalOpen(false)} className="text-gray-500 hover:text-gray-700">Close</button>
            </div>
            <div className="p-6">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b text-sm text-neutral-500">
                    <th className="py-2">Version</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Effective From</th>
                    <th className="py-2">Effective To</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedCalHistory.map(v => (
                    <tr key={v._id || v.id} className="border-b last:border-0 text-sm">
                      <td className="py-3">v{v.version}</td>
                      <td className="py-3">
                        {v.isCurrent ? <StatusBadge status="success" label="Current" /> : <StatusBadge status="neutral" label="Historical" />}
                      </td>
                      <td className="py-3">{v.effectiveFrom ? new Date(v.effectiveFrom).toLocaleDateString() : '-'}</td>
                      <td className="py-3">{v.effectiveTo ? new Date(v.effectiveTo).toLocaleDateString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {dateHistoryModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden">
            <div className="px-6 py-4 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">Holiday Date Version History</h3>
              <button onClick={() => setDateHistoryModalOpen(false)} className="text-gray-500 hover:text-gray-700">Close</button>
            </div>
            <div className="p-6">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b text-sm text-neutral-500">
                    <th className="py-2">Version</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedDateHistory.map(v => (
                    <tr key={v._id || v.id} className="border-b last:border-0 text-sm">
                      <td className="py-3">v{v.version}</td>
                      <td className="py-3">
                        {v.isCurrent ? <StatusBadge status="success" label="Current" /> : <StatusBadge status="neutral" label="Historical" />}
                      </td>
                      <td className="py-3">{new Date(v.holidayDate).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminHolidays;
