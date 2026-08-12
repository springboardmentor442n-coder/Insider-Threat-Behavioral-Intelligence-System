import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const THEME_STORAGE_KEY = "theme";

const ThemeContext = createContext(null);

function readStoredTheme() {
  if (typeof window === "undefined") {
    return "dark";
  }

  const stored = localStorage.getItem(
    THEME_STORAGE_KEY
  );

  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return "dark";
}

function applyThemeClass(theme) {
  if (theme === "light") {
    document.documentElement.classList.add("light");
    document.documentElement.classList.remove("dark");
  } else {
    document.documentElement.classList.add("dark");
    document.documentElement.classList.remove("light");
  }
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(
    readStoredTheme
  );

  useEffect(() => {
    applyThemeClass(theme);

    localStorage.setItem(
      THEME_STORAGE_KEY,
      theme
    );
  }, [theme]);

  const setTheme = useCallback((nextTheme) => {
    setThemeState(nextTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((current) =>
      current === "dark"
        ? "light"
        : "dark"
    );
  }, []);

  const value = useMemo(
    () => ({
      theme,
      isDark: theme === "dark",
      setTheme,
      toggleTheme,
    }),
    [theme, setTheme, toggleTheme]
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error(
      "useTheme must be used inside ThemeProvider."
    );
  }

  return context;
}

export default ThemeContext;
