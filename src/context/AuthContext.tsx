import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getStoredUser } from '../lib/api';
import { getCurrentUser, login as apiLogin, logout as apiLogout, UserProfile, changePassword as apiChangePassword } from '../services/authService';

interface AuthContextValue {
  user: UserProfile | null;
  tokenReady: boolean;
  login: (empId: string, password: string) => Promise<{ mustChangePassword: boolean; role: 'Employee' | 'Admin' }>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(getStoredUser<UserProfile>());
  const [tokenReady, setTokenReady] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        setUser(getStoredUser<UserProfile>());
      } finally {
        setTokenReady(true);
      }
    };

    bootstrap();
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    tokenReady,
    isAuthenticated: Boolean(user),
    login: async (empId, password) => {
      const response = await apiLogin(empId, password);
      setUser({ empId: response.empId, role: response.role, firstLogin: response.firstLogin });
      return { mustChangePassword: response.mustChangePassword, role: response.role };
    },
    changePassword: async (currentPassword, newPassword) => {
      await apiChangePassword(currentPassword, newPassword);
      const refreshedUser = await getCurrentUser();
      setUser(refreshedUser);
    },
    logout: () => {
      apiLogout();
      setUser(null);
    },
    refreshUser: async () => {
      const refreshedUser = await getCurrentUser();
      setUser(refreshedUser);
    },
  }), [user, tokenReady]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
