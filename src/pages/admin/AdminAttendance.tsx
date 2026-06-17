import React from 'react';
import { GlassCard } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';

export const AdminAttendance: React.FC = () => {
  return (
    <DashboardLayout isAdmin>
      <GlassCard className="p-6">
        <h2 className="text-xl font-bold text-neutral-900 mb-4">Attendance Monitor</h2>
        <p>Attendance monitor page coming soon.</p>
      </GlassCard>
    </DashboardLayout>
  );
};

export default AdminAttendance;
