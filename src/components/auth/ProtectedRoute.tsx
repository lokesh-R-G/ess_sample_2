import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function ProtectedRoute({
  children,
  allowRoles,
}: {
  children: React.ReactNode;
  allowRoles?: Array<'Employee' | 'Admin'>;
}) {
  const location = useLocation();
  const { isAuthenticated, tokenReady, user } = useAuth();

  if (!tokenReady) return <div className="min-h-screen bg-white" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.firstLogin && location.pathname !== '/change-password') return <Navigate to="/change-password" replace />;
  if (allowRoles && user && !allowRoles.includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}
