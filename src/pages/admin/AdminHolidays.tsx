import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton, Input } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { api } from '../../lib/api';

export const AdminHolidays: React.FC = () => {
  const [holidays, setHolidays] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [newHoliday, setNewHoliday] = useState({ name: '', date: '', type: 'National' });

  const fetchHolidays = async () => {
    setLoading(true);
    try {
      const data = await api.get<any[]>('/admin/holidays');
      setHolidays(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHolidays();
  }, []);

  const handleAddHoliday = async () => {
    try {
      await api.post('/admin/holidays', newHoliday);
      setNewHoliday({ name: '', date: '', type: 'National' });
      fetchHolidays();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <GlassCard className="p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4">Manage Holidays</h2>
          
          <div className="flex gap-4 mb-6 items-end">
            <div className="flex-1">
              <Input label="Holiday Name" value={newHoliday.name} onChange={e => setNewHoliday({...newHoliday, name: e.target.value})} />
            </div>
            <div className="flex-1">
              <Input label="Date (YYYY-MM-DD)" type="date" value={newHoliday.date} onChange={e => setNewHoliday({...newHoliday, date: e.target.value})} />
            </div>
            <AnimatedButton onClick={handleAddHoliday} disabled={!newHoliday.name || !newHoliday.date}>Add Holiday</AnimatedButton>
          </div>

          {loading ? (
            <p>Loading holidays...</p>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Name</th>
                  <th className="py-3 px-4">Type</th>
                </tr>
              </thead>
              <tbody>
                {holidays.map((hol) => (
                  <tr key={hol.id || hol.date} className="border-b border-neutral-100">
                    <td className="py-3 px-4">{hol.date}</td>
                    <td className="py-3 px-4">{hol.name}</td>
                    <td className="py-3 px-4">{hol.type}</td>
                  </tr>
                ))}
                {holidays.length === 0 && (
                  <tr>
                    <td colSpan={3} className="py-4 text-center text-neutral-500">No holidays found or API not connected.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </GlassCard>
      </div>
    </DashboardLayout>
  );
};

export default AdminHolidays;
