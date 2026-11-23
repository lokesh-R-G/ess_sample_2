import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { UserProfile } from '../types/auth';
import { getCurrentUser, login as apiLogin, logout as apiLogout, changePassword as apiChangePassword } from '../services/authService';
import { getStoredUser, clearAuthStorage } from '../api/client';

interface AuthContextValue {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (empId: string, password: string) => Promise<{ mustChangePassword: boolean; role: 'Employee' | 'Admin' }>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  hasPermission: (permissionId: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const cached = await getStoredUser<UserProfile>();
        if (cached) {
          setUser(cached);
        }
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        // If not authenticated or token expired, keep user null
      } finally {
        setIsLoading(false);
      }
    };
    bootstrap();
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isLoading,
    isAuthenticated: Boolean(user),
    login: async (empId: string, password: string) => {
      const response = await apiLogin(empId, password);
      try {
        const fullUser = await getCurrentUser();
        setUser(fullUser);
      } catch {
        setUser({
          empId: response.empId,
          employeeId: response.employeeId ?? undefined,
          employeeCode: response.employeeCode ?? undefined,
          role: response.role,
          firstLogin: response.firstLogin,
        });
      }
      return { mustChangePassword: response.mustChangePassword, role: response.role };
    },
    changePassword: async (currentPassword: string, newPassword: string) => {
      await apiChangePassword(currentPassword, newPassword);
      const refreshedUser = await getCurrentUser();
      setUser(refreshedUser);
    },
    logout: async () => {
      await apiLogout();
      await clearAuthStorage();
      setUser(null);
    },
    refreshUser: async () => {
      const refreshedUser = await getCurrentUser();
      setUser(refreshedUser);
    },
    hasPermission: (permissionId: string) => {
      if (!user || !user.permissions) return false;
      const scopes = user.permissions[permissionId];
      if (!Array.isArray(scopes) || scopes.length === 0) return false;
      if (scopes.length === 1 && scopes[0] === 'SELF') return false;
      return true;
    },
  }), [user, isLoading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
