import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import authService from "../services/auth/authService";
import tokenService from "../services/auth/tokenService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ============================================================
  // Clear authentication
  // ============================================================

  const clearAuth = useCallback(() => {
    tokenService.clearTokens();
    setUser(null);
  }, []);

  // ============================================================
  // Load currently authenticated user
  // ============================================================

  const loadCurrentUser = useCallback(async () => {
    const token = tokenService.getAccessToken();

    // No token means the user is not logged in.
    if (!token) {
      setUser(null);
      setLoading(false);
      return null;
    }

    try {
      setLoading(true);

      const currentUser = await authService.me();

      setUser(currentUser);

      return currentUser;
    } catch (error) {
      console.error(
        "Failed to load current user:",
        error
      );

      clearAuth();

      return null;
    } finally {
      setLoading(false);
    }
  }, [clearAuth]);

  // ============================================================
  // Check existing session when application starts
  // ============================================================

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  // ============================================================
  // Login
  // ============================================================

  const login = useCallback(
    async (username, password) => {
      /*
       * authService.login():
       * 1. Sends credentials to backend
       * 2. Receives JWT
       * 3. Stores access token
       */
      await authService.login(
        username,
        password
      );

      /*
       * IMPORTANT:
       *
       * Immediately fetch /auth/me.
       *
       * This updates AuthProvider's user state,
       * which makes ProtectedRoute recognize the
       * newly authenticated user.
       */
      const currentUser =
        await loadCurrentUser();

      if (!currentUser) {
        throw new Error(
          "Login succeeded, but the authenticated user could not be loaded."
        );
      }

      return currentUser;
    },
    [loadCurrentUser]
  );

  // ============================================================
  // Logout
  // ============================================================

  const logout = useCallback(() => {
    authService.logout();

    setUser(null);

    /*
     * Force navigation to login.
     */
    window.location.href = "/login";
  }, []);

  // ============================================================
  // Context value
  // ============================================================

  const value = useMemo(
    () => ({
      user,

      loading,

      isAuthenticated:
        Boolean(user),

      login,

      logout,

      refreshUser:
        loadCurrentUser,
    }),
    [
      user,
      loading,
      login,
      logout,
      loadCurrentUser,
    ]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================
// useAuth hook
// ============================================================

export function useAuth() {
  const context = useContext(
    AuthContext
  );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider."
    );
  }

  return context;
}

export default AuthContext;
