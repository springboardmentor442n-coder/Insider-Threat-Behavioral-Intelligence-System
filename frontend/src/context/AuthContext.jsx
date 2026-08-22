import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { auth, getAccessToken, clearTokens } from '../lib/api';

const AuthContext = createContext(null);

// The four roles from the backend, in privilege order. Used to decide which
// dashboard a user lands on and what they may see.
export const ROLES = {
  SECURITY_ANALYST: 'security_analyst',
  SOC_ENGINEER: 'soc_engineer',
  SECURITY_MANAGER: 'security_manager',
  ADMINISTRATOR: 'administrator',
};

export const ROLE_LABEL = {
  security_analyst: 'Security Analyst',
  soc_engineer: 'SOC Engineer',
  security_manager: 'Security Manager',
  administrator: 'Administrator',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, if we have a token, ask the backend who we are. This survives
  // page refreshes without forcing a re-login.
  useEffect(() => {
    let alive = true;
    (async () => {
      if (!getAccessToken()) { setLoading(false); return; }
      try {
        const me = await auth.me();
        if (alive) setUser(me);
      } catch {
        clearTokens();
        if (alive) setUser(null);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  const login = useCallback(async (email, password) => {
    await auth.login(email, password);
    const me = await auth.me();
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(async () => {
    await auth.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
