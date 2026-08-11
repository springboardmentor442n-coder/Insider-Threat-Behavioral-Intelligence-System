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
} from "lucide-react";

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../providers/AuthProvider";

import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "../../features/notifications/hooks/useNotifications";

export default function TopNavbar() {
  const navigate = useNavigate();

  const { user, logout } = useAuth();

  // ============================================================
  // USER
  // ============================================================

  const username = user?.username || "User";

  const role = user?.role
    ? user.role.charAt(0).toUpperCase() +
      user.role.slice(1)
    : "Security Analyst";

  const initial = username
    .charAt(0)
    .toUpperCase();

  // ============================================================
  // NOTIFICATIONS
  // ============================================================

  const {
    data: notificationData,
    isLoading: notificationsLoading,
    isError: notificationsError,
  } = useNotifications();

  const markNotificationRead =
    useMarkNotificationRead();

  const markAllNotificationsRead =
    useMarkAllNotificationsRead();

  const notifications =
    notificationData?.notifications || [];

  const unreadCount =
    notificationData?.unread_count || 0;

  // ============================================================
  // UI STATE
  // ============================================================

  const [searchTerm, setSearchTerm] =
    useState("");

  const [searchOpen, setSearchOpen] =
    useState(false);

  const [notificationsOpen, setNotificationsOpen] =
    useState(false);

  const [userMenuOpen, setUserMenuOpen] =
    useState(false);

  // ============================================================
  // THEME STATE
  //
  // This controls the application root class.
  // The CSS changes below are handled globally.
  // ============================================================

  const [isDark, setIsDark] = useState(() => {
    const savedTheme =
      localStorage.getItem("sentinel-theme");

    if (savedTheme === "light") {
      return false;
    }

    return true;
  });

  // ============================================================
  // REFS
  // ============================================================

  const searchRef = useRef(null);

  const notificationRef =
    useRef(null);

  const userMenuRef =
    useRef(null);

  // ============================================================
  // APPLY THEME
  // ============================================================

  useEffect(() => {
    const root =
      document.documentElement;

    if (isDark) {
      root.classList.add("dark");
      root.classList.remove("light");

      localStorage.setItem(
        "sentinel-theme",
        "dark"
      );
    } else {
      root.classList.add("light");
      root.classList.remove("dark");

      localStorage.setItem(
        "sentinel-theme",
        "light"
      );
    }
  }, [isDark]);

  // ============================================================
  // SEARCHABLE APPLICATION MODULES
  // ============================================================

  const searchablePages = [
    {
      title: "Dashboard",
      description:
        "Security intelligence overview",
      path: "/dashboard",
      icon: ShieldAlert,
      keywords: [
        "dashboard",
        "home",
        "overview",
      ],
    },
    {
      title: "Threat Center",
      description:
        "Detected threats and security events",
      path: "/threats",
      icon: ShieldAlert,
      keywords: [
        "threat",
        "threats",
        "security",
        "risk",
        "alert",
      ],
    },
    {
      title: "Employees",
      description:
        "Employee behavioral information",
      path: "/employees",
      icon: Users,
      keywords: [
        "employee",
        "employees",
        "user",
        "users",
        "staff",
      ],
    },
    {
      title: "Analytics",
      description:
        "Behavioral analytics and insights",
      path: "/analytics",
      icon: Activity,
      keywords: [
        "analytics",
        "analysis",
        "insights",
        "statistics",
      ],
    },
    {
      title: "Models",
      description:
        "Machine learning models",
      path: "/models",
      icon: Brain,
      keywords: [
        "model",
        "models",
        "machine learning",
        "ml",
        "ai",
      ],
    },
    {
      title: "Investigation",
      description:
        "Investigate suspicious activity",
      path: "/investigation",
      icon: Search,
      keywords: [
        "investigation",
        "investigate",
        "case",
        "cases",
      ],
    },
    {
      title: "Reports",
      description:
        "Security reports",
      path: "/reports",
      icon: FileText,
      keywords: [
        "report",
        "reports",
        "document",
      ],
    },
    {
      title: "Settings",
      description:
        "Application settings",
      path: "/settings",
      icon: Settings,
      keywords: [
        "settings",
        "preferences",
        "account",
      ],
    },
  ];

  const filteredResults =
    searchTerm.trim().length > 0
      ? searchablePages
          .filter((item) => {
            const query =
              searchTerm
                .toLowerCase()
                .trim();

            return (
              item.title
                .toLowerCase()
                .includes(query) ||
              item.description
                .toLowerCase()
                .includes(query) ||
              item.keywords.some(
                (keyword) =>
                  keyword
                    .toLowerCase()
                    .includes(query)
              )
            );
          })
          .slice(0, 6)
      : [];

  // ============================================================
  // OUTSIDE CLICK
  // ============================================================

  useEffect(() => {
    const handleOutsideClick = (
      event
    ) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(
          event.target
        )
      ) {
        setSearchOpen(false);
      }

      if (
        notificationRef.current &&
        !notificationRef.current.contains(
          event.target
        )
      ) {
        setNotificationsOpen(false);
      }

      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(
          event.target
        )
      ) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  // ============================================================
  // ESCAPE KEY
  // ============================================================

  useEffect(() => {
    const handleEscape = (
      event
    ) => {
      if (event.key !== "Escape") {
        return;
      }

      setSearchOpen(false);
      setNotificationsOpen(false);
      setUserMenuOpen(false);
    };

    document.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleEscape
      );
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

  // ============================================================
  // SEARCH
  // ============================================================

  const handleSearchSubmit = (
    event
  ) => {
    event.preventDefault();

    if (!filteredResults.length) {
      return;
    }

    goTo(
      filteredResults[0].path
    );

    setSearchTerm("");
  };

  // ============================================================
  // NOTIFICATION ICON
  // ============================================================

  const getNotificationIcon = (
    notification
  ) => {
    switch (
      notification.notification_type
    ) {
      case "threat":
        return ShieldAlert;

      case "risk":
        return AlertTriangle;

      case "activity":
        return Activity;

      case "report":
        return FileText;

      default:
        return Bell;
    }
  };

  // ============================================================
  // NOTIFICATION NAVIGATION
  // ============================================================

  const getNotificationPath = (
    notification
  ) => {
    switch (
      notification.source_type
    ) {
      case "threat":
        return "/threats";

      case "risk":
        return "/employees";

      case "activity":
        return "/investigation";

      case "report":
        return "/reports";

      default:
        return "/dashboard";
    }
  };

  // ============================================================
  // OPEN NOTIFICATION
  // ============================================================

  const handleNotificationClick =
    async (notification) => {
      try {
        if (!notification.is_read) {
          await markNotificationRead.mutateAsync(
            notification.id
          );
        }

        goTo(
          getNotificationPath(
            notification
          )
        );
      } catch (error) {
        console.error(
          "Failed to open notification:",
          error
        );
      }
    };

  // ============================================================
  // MARK ALL READ
  // ============================================================

  const handleMarkAllRead =
    async () => {
      if (unreadCount === 0) {
        return;
      }

      try {
        await markAllNotificationsRead.mutateAsync();
      } catch (error) {
        console.error(
          "Failed to mark notifications as read:",
          error
        );
      }
    };

  // ============================================================
  // NOTIFICATION TIME
  // ============================================================

  const formatNotificationTime = (
    value
  ) => {
    if (!value) {
      return "";
    }

    const date =
      new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "";
    }

    const now =
      new Date();

    const difference =
      now.getTime() -
      date.getTime();

    const seconds =
      Math.floor(
        difference / 1000
      );

    if (seconds < 60) {
      return "Just now";
    }

    const minutes =
      Math.floor(
        seconds / 60
      );

    if (minutes < 60) {
      return `${minutes}m ago`;
    }

    const hours =
      Math.floor(
        minutes / 60
      );

    if (hours < 24) {
      return `${hours}h ago`;
    }

    const days =
      Math.floor(
        hours / 24
      );

    if (days < 7) {
      return `${days}d ago`;
    }

    return date.toLocaleDateString(
      undefined,
      {
        day: "numeric",
        month: "short",
        year: "numeric",
      }
    );
  };

  // ============================================================
  // SEVERITY
  // ============================================================

  const getSeverityClasses = (
    severity
  ) => {
    switch (
      severity?.toLowerCase()
    ) {
      case "critical":
        return {
          icon:
            "bg-red-500/10 text-red-400",
          dot:
            "bg-red-500",
        };

      case "high":
        return {
          icon:
            "bg-orange-500/10 text-orange-400",
          dot:
            "bg-orange-500",
        };

      case "medium":
        return {
          icon:
            "bg-yellow-500/10 text-yellow-400",
          dot:
            "bg-yellow-500",
        };

      default:
        return {
          icon:
            "bg-cyan-500/10 text-cyan-400",
          dot:
            "bg-cyan-500",
        };
    }
  };

  // ============================================================
  // LOGOUT
  // ============================================================

  const handleLogout = () => {
    setUserMenuOpen(false);
    setNotificationsOpen(false);
    setSearchOpen(false);

    logout();
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <header
      className="
        relative
        z-40
        flex
        min-h-[80px]
        w-full
        items-center
        justify-between
        gap-4
        border-b
        border-slate-800/70
        bg-slate-950/35
        px-4
        py-3
        backdrop-blur-xl
        sm:px-6
        lg:px-8
      "
    >
      {/* ======================================================
          SEARCH
          ====================================================== */}

      <div
        ref={searchRef}
        className="
          relative
          min-w-0
          flex-1
        "
      >
        <form
          onSubmit={
            handleSearchSubmit
          }
          className="
            relative
            w-full
            max-w-[560px]
          "
        >
          <Search
            size={20}
            className="
              pointer-events-none
              absolute
              left-4
              top-1/2
              -translate-y-1/2
              text-slate-500
            "
          />

          <input
            type="text"
            value={searchTerm}
            onChange={(event) => {
              const value =
                event.target.value;

              setSearchTerm(value);

              setSearchOpen(
                value.trim().length > 0
              );
            }}
            onFocus={() => {
              if (
                searchTerm.trim()
                  .length > 0
              ) {
                setSearchOpen(true);
              }
            }}
            placeholder="Search employees, threats, reports..."
            aria-label="Search application"
            className="
              h-12
              w-full
              rounded-2xl
              border
              border-slate-700/80
              bg-slate-950/35
              pl-12
              pr-12
              text-sm
              text-slate-200
              outline-none
              placeholder:text-slate-500
              transition
              focus:border-cyan-500/60
              focus:bg-slate-950/50
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
              className="
                absolute
                right-3
                top-1/2
                flex
                h-8
                w-8
                -translate-y-1/2
                items-center
                justify-center
                rounded-lg
                text-slate-500
                hover:bg-slate-800
                hover:text-slate-200
              "
            >
              <X size={17} />
            </button>
          )}
        </form>

        {/* SEARCH RESULTS */}

        {searchOpen && (
          <div
            className="
              absolute
              left-0
              top-[60px]
              z-50
              w-full
              max-w-[560px]
              overflow-hidden
              rounded-2xl
              border
              border-slate-700/80
              bg-slate-950/95
              shadow-2xl
              shadow-black/40
              backdrop-blur-2xl
            "
          >
            {filteredResults.length > 0 ? (
              <div className="p-2">
                <div className="px-3 py-2">
                  <p
                    className="
                      text-[11px]
                      font-semibold
                      uppercase
                      tracking-wider
                      text-slate-500
                    "
                  >
                    Navigation Results
                  </p>
                </div>

                {filteredResults.map(
                  (item) => {
                    const Icon =
                      item.icon;

                    return (
                      <button
                        key={
                          item.path
                        }
                        type="button"
                        onClick={() => {
                          goTo(
                            item.path
                          );

                          setSearchTerm("");
                        }}
                        className="
                          flex
                          w-full
                          items-center
                          gap-3
                          rounded-xl
                          px-3
                          py-3
                          text-left
                          transition
                          hover:bg-cyan-500/10
                        "
                      >
                        <div
                          className="
                            flex
                            h-10
                            w-10
                            shrink-0
                            items-center
                            justify-center
                            rounded-xl
                            border
                            border-cyan-500/15
                            bg-cyan-500/10
                            text-cyan-300
                          "
                        >
                          <Icon size={18} />
                        </div>

                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-white">
                            {item.title}
                          </p>

                          <p className="truncate text-xs text-slate-500">
                            {
                              item.description
                            }
                          </p>
                        </div>
                      </button>
                    );
                  }
                )}
              </div>
            ) : (
              <div className="px-5 py-8 text-center">
                <Search
                  size={24}
                  className="mx-auto mb-2 text-slate-600"
                />

                <p className="text-sm font-medium text-slate-300">
                  No matching section found
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ======================================================
          RIGHT CONTROLS
          ====================================================== */}

      <div
        className="
          flex
          shrink-0
          items-center
          gap-2
          sm:gap-3
        "
      >
        {/* ====================================================
            NOTIFICATIONS
            ==================================================== */}

        <div
          ref={notificationRef}
          className="relative"
        >
          <button
            type="button"
            title="Notifications"
            aria-label="Notifications"
            aria-expanded={
              notificationsOpen
            }
            onClick={() => {
              setNotificationsOpen(
                (value) => !value
              );

              setSearchOpen(false);
              setUserMenuOpen(false);
            }}
            className="
              relative
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-2xl
              border
              border-transparent
              bg-slate-950/25
              text-slate-200
              transition
              hover:border-cyan-500/20
              hover:bg-cyan-500/10
              hover:text-cyan-300
            "
          >
            <Bell size={21} />

            {/* REAL BACKEND-DRIVEN BADGE */}

            {unreadCount > 0 && (
              <>
                <span
                  className="
                    absolute
                    right-2.5
                    top-2
                    h-2.5
                    w-2.5
                    rounded-full
                    bg-red-500
                    ring-2
                    ring-slate-950
                  "
                />

                <span
                  className="
                    absolute
                    -right-1
                    -top-1
                    flex
                    min-h-[18px]
                    min-w-[18px]
                    items-center
                    justify-center
                    rounded-full
                    border
                    border-slate-950
                    bg-red-500
                    px-1
                    text-[9px]
                    font-bold
                    text-white
                  "
                >
                  {unreadCount > 99
                    ? "99+"
                    : unreadCount}
                </span>
              </>
            )}
          </button>

          {/* NOTIFICATION PANEL */}

          {notificationsOpen && (
            <div
              className="
                absolute
                right-0
                top-[54px]
                z-50
                w-[390px]
                max-w-[calc(100vw-24px)]
                overflow-hidden
                rounded-2xl
                border
                border-slate-700/80
                bg-slate-950/95
                shadow-2xl
                shadow-black/50
                backdrop-blur-2xl
              "
            >
              <div
                className="
                  flex
                  items-center
                  justify-between
                  border-b
                  border-slate-800
                  px-4
                  py-4
                "
              >
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-white">
                      Notifications
                    </p>

                    {unreadCount > 0 && (
                      <span
                        className="
                          rounded-full
                          bg-red-500/15
                          px-2
                          py-0.5
                          text-[10px]
                          font-semibold
                          text-red-400
                        "
                      >
                        {unreadCount} unread
                      </span>
                    )}
                  </div>

                  <p className="mt-1 text-xs text-slate-500">
                    Security events requiring attention
                  </p>
                </div>

                {unreadCount > 0 && (
                  <button
                    type="button"
                    onClick={
                      handleMarkAllRead
                    }
                    disabled={
                      markAllNotificationsRead.isPending
                    }
                    className="
                      flex
                      items-center
                      gap-1.5
                      rounded-lg
                      px-2
                      py-1.5
                      text-[11px]
                      font-medium
                      text-cyan-400
                      transition
                      hover:bg-cyan-500/10
                      disabled:opacity-50
                    "
                  >
                    <CheckCheck
                      size={14}
                    />

                    Mark all read
                  </button>
                )}
              </div>

              <div
                className="
                  max-h-[480px]
                  overflow-y-auto
                "
              >
                {notificationsLoading ? (
                  <div className="px-5 py-10 text-center">
                    <div
                      className="
                        mx-auto
                        mb-3
                        h-7
                        w-7
                        animate-spin
                        rounded-full
                        border-2
                        border-slate-700
                        border-t-cyan-400
                      "
                    />

                    <p className="text-xs text-slate-500">
                      Loading security events...
                    </p>
                  </div>
                ) : notificationsError ? (
                  <div className="px-5 py-10 text-center">
                    <AlertTriangle
                      size={25}
                      className="mx-auto mb-3 text-red-400"
                    />

                    <p className="text-sm font-medium text-slate-300">
                      Unable to load notifications
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      The notification service could not be reached.
                    </p>
                  </div>
                ) : notifications.length ===
                  0 ? (
                  <div className="px-5 py-12 text-center">
                    <div
                      className="
                        mx-auto
                        mb-3
                        flex
                        h-12
                        w-12
                        items-center
                        justify-center
                        rounded-full
                        bg-emerald-500/10
                      "
                    >
                      <Check
                        size={23}
                        className="text-emerald-400"
                      />
                    </div>

                    <p className="text-sm font-medium text-slate-300">
                      You're all caught up
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      No security notifications at the moment.
                    </p>
                  </div>
                ) : (
                  <div className="p-2">
                    {notifications.map(
                      (notification) => {
                        const Icon =
                          getNotificationIcon(
                            notification
                          );

                        const severity =
                          getSeverityClasses(
                            notification.severity
                          );

                        return (
                          <button
                            key={
                              notification.id
                            }
                            type="button"
                            onClick={() =>
                              handleNotificationClick(
                                notification
                              )
                            }
                            className={`
                              group
                              flex
                              w-full
                              items-start
                              gap-3
                              rounded-xl
                              p-3
                              text-left
                              transition
                              hover:bg-slate-800/60
                              ${
                                notification.is_read
                                  ? ""
                                  : "bg-cyan-500/[0.035]"
                              }
                            `}
                          >
                            <div
                              className={`
                                mt-0.5
                                flex
                                h-10
                                w-10
                                shrink-0
                                items-center
                                justify-center
                                rounded-xl
                                ${severity.icon}
                              `}
                            >
                              <Icon
                                size={18}
                              />
                            </div>

                            <div className="min-w-0 flex-1">
                              <div className="flex items-start justify-between gap-2">
                                <p
                                  className={
                                    notification.is_read
                                      ? "text-sm font-medium text-slate-300"
                                      : "text-sm font-semibold text-white"
                                  }
                                >
                                  {
                                    notification.title
                                  }
                                </p>

                                {!notification.is_read && (
                                  <span
                                    className={`
                                      mt-1
                                      h-2
                                      w-2
                                      shrink-0
                                      rounded-full
                                      ${severity.dot}
                                    `}
                                  />
                                )}
                              </div>

                              <p className="mt-1 text-xs leading-5 text-slate-400">
                                {
                                  notification.message
                                }
                              </p>

                              <div className="mt-2 flex items-center gap-2">
                                <span className="text-[10px] text-slate-500">
                                  {formatNotificationTime(
                                    notification.event_created_at
                                  )}
                                </span>

                                {notification.is_read && (
                                  <span className="flex items-center gap-1 text-[10px] text-slate-500">
                                    <Check
                                      size={11}
                                    />
                                    Read
                                  </span>
                                )}
                              </div>
                            </div>
                          </button>
                        );
                      }
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ====================================================
            REAL THEME TOGGLE
            ==================================================== */}

        <button
          type="button"
          title={
            isDark
              ? "Switch to light theme"
              : "Switch to dark theme"
          }
          aria-label={
            isDark
              ? "Switch to light theme"
              : "Switch to dark theme"
          }
          onClick={() =>
            setIsDark(
              (value) => !value
            )
          }
          className="
            flex
            h-11
            w-11
            items-center
            justify-center
            rounded-2xl
            border
            border-transparent
            bg-slate-950/25
            text-slate-200
            transition
            hover:border-cyan-500/20
            hover:bg-cyan-500/10
            hover:text-cyan-300
          "
        >
          {isDark ? (
            <Moon size={21} />
          ) : (
            <Sun size={21} />
          )}
        </button>

        {/* ====================================================
            USER MENU
            ==================================================== */}

        <div
          ref={userMenuRef}
          className="relative"
        >
          <button
            type="button"
            onClick={() => {
              setUserMenuOpen(
                (value) => !value
              );

              setNotificationsOpen(false);
              setSearchOpen(false);
            }}
            className="
              ml-1
              flex
              items-center
              gap-2
              rounded-2xl
              bg-slate-950/20
              px-2
              py-1.5
              transition
              hover:bg-slate-900/50
              sm:gap-3
              sm:px-3
            "
          >
            <div
              className="
                flex
                h-11
                w-11
                shrink-0
                items-center
                justify-center
                rounded-full
                bg-gradient-to-r
                from-cyan-400
                to-blue-600
                text-sm
                font-bold
                text-white
                shadow-lg
                shadow-cyan-500/20
              "
            >
              {initial}
            </div>

            <div className="hidden min-w-0 sm:block">
              <p className="max-w-[150px] truncate text-sm font-semibold text-white">
                {username}
              </p>

              <p className="text-xs text-slate-400">
                {role}
              </p>
            </div>

            <ChevronDown
              size={16}
              className={`
                hidden
                text-slate-500
                transition-transform
                sm:block
                ${
                  userMenuOpen
                    ? "rotate-180"
                    : ""
                }
              `}
            />
          </button>

          {userMenuOpen && (
            <div
              className="
                absolute
                right-0
                top-[58px]
                z-50
                w-[270px]
                overflow-hidden
                rounded-2xl
                border
                border-slate-700/80
                bg-slate-950/95
                shadow-2xl
                shadow-black/50
                backdrop-blur-2xl
              "
            >
              <div
                className="
                  border-b
                  border-slate-800
                  bg-slate-900/30
                  px-4
                  py-4
                "
              >
                <div className="flex items-center gap-3">
                  <div
                    className="
                      flex
                      h-11
                      w-11
                      items-center
                      justify-center
                      rounded-full
                      bg-gradient-to-r
                      from-cyan-400
                      to-blue-600
                      text-sm
                      font-bold
                      text-white
                    "
                  >
                    {initial}
                  </div>

                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-white">
                      {username}
                    </p>

                    <p className="text-xs text-cyan-400">
                      {role}
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-2">
                <button
                  type="button"
                  onClick={() =>
                    goTo("/settings")
                  }
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    rounded-xl
                    px-3
                    py-3
                    text-left
                    text-sm
                    text-slate-300
                    transition
                    hover:bg-cyan-500/10
                    hover:text-white
                  "
                >
                  <User
                    size={18}
                    className="text-cyan-400"
                  />

                  <div>
                    <p className="font-medium">
                      Profile
                    </p>

                    <p className="text-xs text-slate-500">
                      View account information
                    </p>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    goTo("/settings")
                  }
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    rounded-xl
                    px-3
                    py-3
                    text-left
                    text-sm
                    text-slate-300
                    transition
                    hover:bg-cyan-500/10
                    hover:text-white
                  "
                >
                  <Settings
                    size={18}
                    className="text-cyan-400"
                  />

                  <div>
                    <p className="font-medium">
                      Settings
                    </p>

                    <p className="text-xs text-slate-500">
                      Manage application settings
                    </p>
                  </div>
                </button>

                <div className="my-1 border-t border-slate-800" />

                <button
                  type="button"
                  onClick={
                    handleLogout
                  }
                  className="
                    flex
                    w-full
                    items-center
                    gap-3
                    rounded-xl
                    px-3
                    py-3
                    text-left
                    text-sm
                    text-red-400
                    transition
                    hover:bg-red-500/10
                  "
                >
                  <LogOut size={18} />

                  <div>
                    <p className="font-medium">
                      Logout
                    </p>

                    <p className="text-xs text-red-400/60">
                      End current session
                    </p>
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ====================================================
            DIRECT LOGOUT
            ==================================================== */}

        <button
          type="button"
          title="Logout"
          aria-label="Logout"
          onClick={handleLogout}
          className="
            hidden
            h-11
            w-11
            items-center
            justify-center
            rounded-2xl
            border
            border-red-500/20
            bg-red-500/5
            text-red-400
            transition
            hover:border-red-500/30
            hover:bg-red-500/10
            sm:flex
          "
        >
          <LogOut size={19} />
        </button>
      </div>
    </header>
  );
}
