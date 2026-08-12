import {
  Activity,
  AlertTriangle,
  Bell,
  Brain,
  Check,
  CheckCheck,
  ChevronDown,
  FileText,
  LogOut,
  Moon,
  Search,
  Settings,
  ShieldAlert,
  Sun,
  User,
  Users,
  X,
  ShieldCheck,
} from "lucide-react";

import { useEffect, useRef, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { useAuth } from "../../providers/AuthProvider";
import { useTheme } from "../../providers/ThemeProvider";

import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "../../features/notifications/hooks/useNotifications";

export default function TopNavbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  // ============================================================
  // USER STATE
  // ============================================================

  const username = user?.username || user?.user || "Analyst";

  const role = user?.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : "Security Analyst";

  const initial = username.charAt(0).toUpperCase();

  // ============================================================
  // NOTIFICATIONS
  // ============================================================

  const {
    data: notificationData,
    isLoading: notificationsLoading,
    isError: notificationsError,
  } = useNotifications();

  const markNotificationRead = useMarkNotificationRead();
  const markAllNotificationsRead = useMarkAllNotificationsRead();

  const notifications = notificationData?.notifications || [];
  const unreadCount = notificationData?.unread_count || 0;

  // ============================================================
  // UI STATE
  // ============================================================

  const [searchTerm, setSearchTerm] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // ============================================================
  // REFS
  // ============================================================

  const searchRef = useRef(null);
  const notificationRef = useRef(null);
  const userMenuRef = useRef(null);

  // ============================================================
  // BREADCRUMB CONTEXT
  // ============================================================

  const getBreadcrumb = (path) => {
    if (path.startsWith("/dashboard")) return { category: "Insider Threat Intelligence", page: "Dashboard" };
    if (path.startsWith("/threats")) return { category: "Security Operations", page: "Threat Center" };
    if (path.startsWith("/employees")) return { category: "Employee Intelligence", page: "All Employees" };
    if (path.startsWith("/analytics")) return { category: "Behavioral Intelligence", page: "Analytics" };
    if (path.startsWith("/models")) return { category: "Machine Learning", page: "Ensemble Models" };
    if (path.startsWith("/explainability")) return { category: "Model Intelligence", page: "Explainability" };
    if (path.startsWith("/investigation")) return { category: "Security Operations", page: "Investigation" };
    if (path.startsWith("/reports")) return { category: "Intelligence Reports", page: "Reports Center" };
    if (path.startsWith("/verification")) return { category: "Behavioral Intelligence", page: "CERT Verification" };
    if (path.startsWith("/account")) return { category: "User Identity", page: "My Account" };
    if (path.startsWith("/settings")) return { category: "System Preferences", page: "Settings" };
    return { category: "Security Intelligence", page: "Overview" };
  };

  const breadcrumb = getBreadcrumb(location.pathname);

  // ============================================================
  // SEARCHABLE APPLICATION MODULES
  // ============================================================

  const searchablePages = [
    {
      title: "Dashboard",
      description: "Security intelligence overview",
      path: "/dashboard",
      icon: ShieldAlert,
      keywords: ["dashboard", "home", "overview"],
    },
    {
      title: "Threat Center",
      description: "Detected threats and security events",
      path: "/threats",
      icon: ShieldAlert,
      keywords: ["threat", "threats", "security", "risk", "alert"],
    },
    {
      title: "Employees",
      description: "Employee behavioral information",
      path: "/employees",
      icon: Users,
      keywords: ["employee", "employees", "user", "users", "staff"],
    },
    {
      title: "Analytics",
      description: "Behavioral analytics and insights",
      path: "/analytics",
      icon: Activity,
      keywords: ["analytics", "analysis", "insights", "statistics"],
    },
    {
      title: "Models",
      description: "Machine learning ensemble models",
      path: "/models",
      icon: Brain,
      keywords: ["model", "models", "machine learning", "ml", "ai"],
    },
    {
      title: "Investigation",
      description: "Investigate suspicious activity cases",
      path: "/investigation",
      icon: Search,
      keywords: ["investigation", "investigate", "case", "cases"],
    },
    {
      title: "Reports",
      description: "Security intelligence reports",
      path: "/reports",
      icon: FileText,
      keywords: ["report", "reports", "document", "csv", "pdf"],
    },
    {
      title: "My Account",
      description: "User identity and security access profile",
      path: "/account",
      icon: User,
      keywords: ["account", "profile", "user", "role"],
    },
    {
      title: "Settings",
      description: "System preferences and appearance",
      path: "/settings",
      icon: Settings,
      keywords: ["settings", "preferences", "theme", "appearance"],
    },
  ];

  const filteredResults =
    searchTerm.trim().length > 0
      ? searchablePages
          .filter((item) => {
            const query = searchTerm.toLowerCase().trim();
            return (
              item.title.toLowerCase().includes(query) ||
              item.description.toLowerCase().includes(query) ||
              item.keywords.some((kw) => kw.toLowerCase().includes(query))
            );
          })
          .slice(0, 5)
      : [];

  // ============================================================
  // OUTSIDE CLICK & ESCAPE KEY HANDLERS
  // ============================================================

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setSearchOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setNotificationsOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setSearchOpen(false);
        setNotificationsOpen(false);
        setUserMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  // ============================================================
  // NAVIGATION
  // ============================================================

  const goTo = (path) => {
    navigate(path);
    setSearchOpen(false);
    setNotificationsOpen(false);
    setUserMenuOpen(false);
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    if (!filteredResults.length) return;
    goTo(filteredResults[0].path);
    setSearchTerm("");
  };

  // ============================================================
  // NOTIFICATION HELPERS
  // ============================================================

  const getNotificationIcon = (notification) => {
    switch (notification.notification_type) {
      case "threat": return ShieldAlert;
      case "risk": return AlertTriangle;
      case "activity": return Activity;
      case "report": return FileText;
      default: return Bell;
    }
  };

  const getNotificationPath = (notification) => {
    switch (notification.source_type) {
      case "threat": return "/threats";
      case "risk": return "/employees";
      case "activity": return "/investigation";
      case "report": return "/reports";
      default: return "/dashboard";
    }
  };

  const handleNotificationClick = async (notification) => {
    try {
      if (!notification.is_read) {
        await markNotificationRead.mutateAsync(notification.id);
      }
      goTo(getNotificationPath(notification));
    } catch (error) {
      console.error("Failed to open notification:", error);
    }
  };

  const handleMarkAllRead = async () => {
    if (unreadCount === 0) return;
    try {
      await markAllNotificationsRead.mutateAsync();
    } catch (error) {
      console.error("Failed to mark notifications as read:", error);
    }
  };

  const formatNotificationTime = (value) => {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    if (diff > 0 && diff < 86400000) {
      const mins = Math.floor(diff / 60000);
      if (mins < 1) return "Just now";
      if (mins < 60) return `${mins}m ago`;
      const hours = Math.floor(mins / 60);
      return `${hours}h ago`;
    }
    return date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
  };

  const getSeverityClasses = (severity) => {
    switch (severity?.toLowerCase()) {
      case "critical": return { icon: "bg-red-500/10 text-red-400", dot: "bg-red-500" };
      case "high": return { icon: "bg-orange-500/10 text-orange-400", dot: "bg-orange-500" };
      case "medium": return { icon: "bg-yellow-500/10 text-yellow-400", dot: "bg-yellow-500" };
      default: return { icon: "bg-cyan-500/10 text-cyan-400", dot: "bg-cyan-500" };
    }
  };

  const handleLogout = () => {
    setUserMenuOpen(false);
    setNotificationsOpen(false);
    setSearchOpen(false);
    logout();
    navigate("/login");
  };

  return (
    <header
      className="
        relative
        z-40
        flex
        h-[56px]
        min-h-[56px]
        w-full
        items-center
        justify-between
        gap-3
        border-b
        border-slate-800/80
        bg-slate-950/80
        px-4
        py-2
        backdrop-blur-xl
        sm:px-6
      "
    >
      {/* ======================================================
          LEFT: BREADCRUMB CONTEXT & SEARCH
          ====================================================== */}

      <div className="flex items-center gap-4 min-w-0 flex-1">
        {/* Compact Breadcrumb */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 shrink-0 font-medium">
          <span className="text-slate-400/80">{breadcrumb.category}</span>
          <span className="text-slate-400/80">/</span>
          <span className="font-bold text-white tracking-tight">{breadcrumb.page}</span>
        </div>

        {/* Search Control */}
        <div ref={searchRef} className="relative min-w-0 flex-1 max-w-[360px] md:max-w-[420px]">
          <form onSubmit={handleSearchSubmit} className="relative w-full">
            <Search
              size={16}
              className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500"
            />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => {
                const val = e.target.value;
                setSearchTerm(val);
                setSearchOpen(val.trim().length > 0);
              }}
              onFocus={() => {
                if (searchTerm.trim().length > 0) setSearchOpen(true);
              }}
              placeholder="Search employees, threats, reports..."
              aria-label="Search application"
              className="
                h-9
                w-full
                rounded-xl
                border
                border-slate-800
                bg-slate-900/60
                pl-10
                pr-9
                text-xs
                text-slate-200
                outline-none
                placeholder:text-slate-500
                transition
                focus:border-cyan-500/50
                focus:bg-slate-900/90
                focus:ring-2
                focus:ring-cyan-500/10
              "
            />
            {searchTerm && (
              <button
                type="button"
                aria-label="Clear search"
                onClick={() => {
                  setSearchTerm("");
                  setSearchOpen(false);
                }}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 flex h-5 w-5 items-center justify-center rounded-md text-slate-500 hover:bg-slate-800 hover:text-slate-200"
              >
                <X size={14} />
              </button>
            )}
          </form>

          {/* Search Dropdown */}
          {searchOpen && (
            <div className="absolute left-0 top-[42px] z-50 w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950/95 shadow-2xl backdrop-blur-2xl">
              {filteredResults.length > 0 ? (
                <div className="p-1.5">
                  <p className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    Quick Navigation
                  </p>
                  {filteredResults.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.path}
                        type="button"
                        onClick={() => {
                          goTo(item.path);
                          setSearchTerm("");
                        }}
                        className="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left transition hover:bg-cyan-500/10"
                      >
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
                          <Icon size={14} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-white">{item.title}</p>
                          <p className="truncate text-[11px] text-slate-400">{item.description}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="px-4 py-6 text-center text-xs text-slate-400">
                  No matching module found
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ======================================================
          RIGHT CONTROLS
          ====================================================== */}

      <div className="flex shrink-0 items-center gap-2">

        {/* System Status Badge */}
        <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>Active ML Feed</span>
        </div>

        {/* Notifications */}
        <div ref={notificationRef} className="relative">
          <button
            type="button"
            title="Notifications"
            aria-label="Notifications"
            aria-expanded={notificationsOpen}
            onClick={() => {
              setNotificationsOpen((val) => !val);
              setSearchOpen(false);
              setUserMenuOpen(false);
            }}
            className="
              relative
              flex
              h-9
              w-9
              items-center
              justify-center
              rounded-xl
              border
              border-slate-800
              bg-slate-900/60
              text-slate-300
              transition
              hover:border-cyan-500/30
              hover:bg-cyan-500/10
              hover:text-cyan-300
            "
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-extrabold text-white ring-2 ring-slate-950">
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {notificationsOpen && (
            <div className="absolute right-0 top-[44px] z-50 w-[360px] max-w-[calc(100vw-24px)] overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/95 shadow-2xl backdrop-blur-2xl">
              <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-bold text-white">Notifications</p>
                  {unreadCount > 0 && (
                    <span className="rounded-full bg-red-500/15 px-2 py-0.5 text-[10px] font-semibold text-red-400">
                      {unreadCount} unread
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    type="button"
                    onClick={handleMarkAllRead}
                    disabled={markAllNotificationsRead.isPending}
                    className="flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium text-cyan-400 transition hover:bg-cyan-500/10 disabled:opacity-50"
                  >
                    <CheckCheck size={13} />
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-[400px] overflow-y-auto">
                {notificationsLoading ? (
                  <div className="py-8 text-center text-xs text-slate-400">
                    Loading security events...
                  </div>
                ) : notificationsError ? (
                  <div className="py-8 text-center text-xs text-red-400">
                    Unable to load notifications
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="py-10 text-center">
                    <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
                      <Check size={20} />
                    </div>
                    <p className="text-xs font-bold text-white">You're all caught up</p>
                    <p className="mt-0.5 text-[11px] text-slate-400">No active security alerts.</p>
                  </div>
                ) : (
                  <div className="p-1.5 space-y-1">
                    {notifications.map((notification) => {
                      const Icon = getNotificationIcon(notification);
                      const severity = getSeverityClasses(notification.severity);
                      return (
                        <button
                          key={notification.id}
                          type="button"
                          onClick={() => handleNotificationClick(notification)}
                          className={`
                            flex
                            w-full
                            items-start
                            gap-2.5
                            rounded-xl
                            p-2.5
                            text-left
                            transition
                            hover:bg-slate-800/60
                            ${notification.is_read ? "" : "bg-cyan-500/[0.04] border border-cyan-500/10"}
                          `}
                        >
                          <div className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${severity.icon}`}>
                            <Icon size={16} />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between gap-1">
                              <p className={`text-xs ${notification.is_read ? "font-medium text-slate-300" : "font-bold text-white"}`}>
                                {notification.title}
                              </p>
                              {!notification.is_read && (
                                <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${severity.dot}`} />
                              )}
                            </div>
                            <p className="mt-0.5 text-[11px] leading-4 text-slate-400 line-clamp-2">
                              {notification.message}
                            </p>
                            <span className="mt-1 block text-[10px] text-slate-400">
                              {formatNotificationTime(notification.event_created_at)}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          type="button"
          title={isDark ? "Switch to light theme" : "Switch to dark theme"}
          aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
          onClick={toggleTheme}
          className="
            flex
            h-9
            w-9
            items-center
            justify-center
            rounded-xl
            border
            border-slate-800
            bg-slate-900/60
            text-slate-300
            transition
            hover:border-cyan-500/30
            hover:bg-cyan-500/10
            hover:text-cyan-300
          "
        >
          {isDark ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        {/* User Profile Menu */}
        <div ref={userMenuRef} className="relative">
          <button
            type="button"
            aria-label="Open profile menu"
            onClick={() => {
              setUserMenuOpen((val) => !val);
              setNotificationsOpen(false);
              setSearchOpen(false);
            }}
            className="
              flex
              items-center
              gap-2
              rounded-xl
              border
              border-slate-800
              bg-slate-900/60
              p-1
              pr-2.5
              transition
              hover:border-cyan-500/30
              hover:bg-slate-900/90
            "
          >
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-r from-cyan-400 to-blue-600 text-xs font-bold text-white shadow-md">
              {initial}
            </div>
            <div className="hidden min-w-0 text-left sm:block">
              <p className="max-w-[110px] truncate text-xs font-bold text-white leading-tight">
                {username}
              </p>
              <p className="text-[10px] text-cyan-400 leading-tight">{role}</p>
            </div>
            <ChevronDown
              size={14}
              className={`hidden text-slate-400 transition-transform sm:block ${userMenuOpen ? "rotate-180" : ""}`}
            />
          </button>

          {/* User Profile Dropdown */}
          {userMenuOpen && (
            <div className="absolute right-0 top-[44px] z-50 w-[240px] overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/95 shadow-2xl backdrop-blur-2xl">
              {/* Profile Header */}
              <div className="border-b border-slate-800/80 bg-slate-900/40 p-3.5">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-xs font-bold text-white shadow-md">
                    {initial}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-xs font-bold text-white">{username}</p>
                    <p className="text-[11px] font-semibold text-cyan-400">{role}</p>
                  </div>
                </div>
              </div>

              <div className="p-1.5 space-y-1">
                {/* Account */}
                <button
                  type="button"
                  onClick={() => goTo("/account")}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs text-slate-300 transition hover:bg-cyan-500/10 hover:text-white"
                >
                  <User size={15} className="text-cyan-400" />
                  <div>
                    <p className="font-semibold">My Account</p>
                    <p className="text-[10px] text-slate-400">View identity & access profile</p>
                  </div>
                </button>

                {/* Settings */}
                <button
                  type="button"
                  onClick={() => goTo("/settings")}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs text-slate-300 transition hover:bg-cyan-500/10 hover:text-white"
                >
                  <Settings size={15} className="text-cyan-400" />
                  <div>
                    <p className="font-semibold">Settings</p>
                    <p className="text-[10px] text-slate-400">System & theme preferences</p>
                  </div>
                </button>

                <div className="my-1 border-t border-slate-800/80" />

                {/* Logout */}
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-xs text-red-400 transition hover:bg-red-500/10"
                >
                  <LogOut size={15} />
                  <div>
                    <p className="font-semibold">Sign Out</p>
                    <p className="text-[10px] text-red-400/70">End security session</p>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
