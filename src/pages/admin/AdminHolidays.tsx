import React, { useEffect, useState } from 'react';
import { Plus, Save, Trash2, Edit2, Calendar } from 'lucide-react';
import { GlassCard, AnimatedButton, Input, StatusBadge } from '../../components/ui';
import { 
  HolidayCalendar, HolidayDate, 
  getHolidayCalendars, createHolidayCalendar, updateHolidayCalendar, deleteHolidayCalendar,
  getHolidayDates, createHolidayDate, updateHolidayDate, deleteHolidayDate 
} from '../../services/holidayCalendarService';

export const AdminHolidays: React.FC = () => {
  const [calendars, setCalendars] = useState<HolidayCalendar[]>([]);
  const [selectedCalendar, setSelectedCalendar] = useState<HolidayCalendar | null>(null);
  const [editingCalendar, setEditingCalendar] = useState<HolidayCalendar | null>(null);
  
  const [dates, setDates] = useState<HolidayDate[]>([]);
  const [editingDate, setEditingDate] = useState<HolidayDate | null>(null);
  
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadCalendars();
  }, []);

  const loadCalendars = async () => {
    try {
      const data = await getHolidayCalendars();
      setCalendars(data);
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
    if (c._id) loadDates(c._id);
  };

  // Calendar CRUD
  const handleSaveCalendar = async () => {
    if (!editingCalendar) return;
    try {
      setIsSaving(true);
      if (editingCalendar._id) {
        await updateHolidayCalendar(editingCalendar._id, editingCalendar);
      } else {
        await createHolidayCalendar(editingCalendar);
      }
      setEditingCalendar(null);
      await loadCalendars();
    } finally {
      setIsSaving(false);
    }
  };

  // Date CRUD
  const handleSaveDate = async () => {
    if (!editingDate || !selectedCalendar?._id) return;
    try {
      setIsSaving(true);
      if (editingDate._id) {
        await updateHolidayDate(selectedCalendar._id, editingDate._id, editingDate);
      } else {
        await createHolidayDate(selectedCalendar._id, editingDate);
      }
      setEditingDate(null);
      await loadDates(selectedCalendar._id);
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
          <AnimatedButton icon={Plus} onClick={() => setEditingCalendar({ name: '', year: new Date().getFullYear() })}>New Calendar</AnimatedButton>
        )}
      </div>

      {editingCalendar && (
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold mb-4">{editingCalendar._id ? 'Edit Calendar' : 'Create Calendar'}</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <Input label="Name" value={editingCalendar.name} onChange={e => setEditingCalendar({...editingCalendar, name: e.target.value})} />
            <Input type="number" label="Year" value={editingCalendar.year} onChange={e => setEditingCalendar({...editingCalendar, year: parseInt(e.target.value)})} />
            <Input label="Description" value={editingCalendar.description || ''} onChange={e => setEditingCalendar({...editingCalendar, description: e.target.value})} />
          </div>
          <div className="flex gap-2 justify-end">
            <AnimatedButton variant="secondary" onClick={() => setEditingCalendar(null)}>Cancel</AnimatedButton>
            <AnimatedButton icon={Save} loading={isSaving} onClick={handleSaveCalendar}>Save Calendar</AnimatedButton>
          </div>
        </GlassCard>
      )}

      {!selectedCalendar && !editingCalendar && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {calendars.map(c => (
            <GlassCard key={c._id} className="p-4 cursor-pointer hover:border-primary-500 transition-colors" onClick={() => handleSelectCalendar(c)}>
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg">{c.name}</h3>
                <StatusBadge status="info" label={c.year.toString()} />
              </div>
              <p className="text-sm text-neutral-500 mb-4">{c.description || 'No description'}</p>
              <div className="flex justify-end gap-2" onClick={e => e.stopPropagation()}>
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
                <AnimatedButton size="sm" icon={Plus} onClick={() => setEditingDate({ calendarId: selectedCalendar._id!, name: '', date: '', type: 'Mandatory' })}>Add Date</AnimatedButton>
              )}
            </div>

            {editingDate && (
              <div className="bg-neutral-50 p-4 rounded-lg border mb-6">
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <Input type="date" label="Date" value={editingDate.date.split('T')[0]} onChange={e => setEditingDate({...editingDate, date: e.target.value})} />
                  <Input label="Holiday Name" value={editingDate.name} onChange={e => setEditingDate({...editingDate, name: e.target.value})} />
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 mb-1">Type</label>
                    <select className="w-full px-4 py-2 bg-white border border-neutral-300 rounded-lg" value={editingDate.type} onChange={e => setEditingDate({...editingDate, type: e.target.value})}>
                      <option value="Mandatory">Mandatory</option>
                      <option value="Restricted">Restricted</option>
                      <option value="Optional">Optional</option>
                    </select>
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <AnimatedButton variant="secondary" size="sm" onClick={() => setEditingDate(null)}>Cancel</AnimatedButton>
                  <AnimatedButton icon={Save} size="sm" loading={isSaving} onClick={handleSaveDate}>Save Date</AnimatedButton>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {dates.map(d => (
                <div key={d._id} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="bg-primary-50 text-primary-700 px-3 py-1 rounded font-medium">{new Date(d.date).toLocaleDateString()}</div>
                    <div className="font-medium text-neutral-900">{d.name}</div>
                    <StatusBadge status={d.type === 'Mandatory' ? 'error' : 'info'} label={d.type} />
                  </div>
                  <div className="flex gap-2">
                    <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={() => setEditingDate(d)}>Edit</AnimatedButton>
                    <AnimatedButton variant="danger" size="sm" icon={Trash2} onClick={async () => {
                      if(confirm('Delete holiday?')) {
                        await deleteHolidayDate(selectedCalendar._id!, d._id!);
                        loadDates(selectedCalendar._id!);
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
    </div>
  );
};

export default AdminHolidays;
