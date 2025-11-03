import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { fetchMe, login as loginRequest, logout as logoutRequest } from '../api/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await fetchMe();
      setUser(data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const handler = () => setUser(null);
    window.addEventListener('unauthenticated', handler);
    return () => window.removeEventListener('unauthenticated', handler);
  }, [refresh]);

  const login = async (credentials) => {
    const data = await loginRequest(credentials);
    setUser(data);
    return data;
  };

  const logout = async () => {
    await logoutRequest();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, refresh }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
