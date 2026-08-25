import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function ProtectedRoute({
  children,
  requireAnyPermission,
}: {
  children: React.ReactNode;
  requireAnyPermission?: string[];
}) {
  const location = useLocation();
  const { isAuthenticated, tokenReady, user, hasPermission } = useAuth();

  if (!tokenReady) return <div className="min-h-screen bg-white" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.firstLogin && location.pathname !== '/change-password') return <Navigate to="/change-password" replace />;
  if (requireAnyPermission && requireAnyPermission.length > 0) {
    const hasAny = requireAnyPermission.some(p => hasPermission(p));
    if (!hasAny) return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}
