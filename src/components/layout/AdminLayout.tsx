import React from 'react';
import { Outlet } from 'react-router-dom';
import DashboardLayout from './DashboardLayout';

export const AdminLayout: React.FC = () => {
  return (
    <DashboardLayout isAdmin>
      <Outlet />
    </DashboardLayout>
  );
};

export default AdminLayout;
