import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';

// Pages
import LoginPage from './pages/auth/LoginPage';
import Dashboard from './pages/employee/Dashboard';
import Attendance from './pages/employee/Attendance';
import LeaveManagement from './pages/employee/LeaveManagement';
import Payslip from './pages/employee/Payslip';
import Profile from './pages/employee/Profile';
import AdminDashboard from './pages/admin/AdminDashboard';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginPage onLogin={handleLogin} />
              )
            }
          />

          {/* Employee Routes */}
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/attendance"
            element={
              isAuthenticated ? (
                <Attendance />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/leave"
            element={
              isAuthenticated ? (
                <LeaveManagement />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/payslip"
            element={
              isAuthenticated ? (
                <Payslip />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/profile"
            element={
              isAuthenticated ? (
                <Profile />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/reports"
            element={
              isAuthenticated ? (
                <Dashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/employees"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/payroll"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/branches"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/attendance"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/approvals"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/admin/settings"
            element={
              isAuthenticated ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />

          {/* Default Routes */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
