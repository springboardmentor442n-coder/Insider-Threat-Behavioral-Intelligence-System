import { Link, NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  TriangleAlert,
  Users,
  BarChart3,
  BrainCircuit,
  Sparkles,
  Search,
  FileText,
  ShieldCheck,
  Settings,
  UserPlus,
  UserCheck,
} from "lucide-react";

import { useAuth } from "../../providers/AuthProvider";

const allMenuItems = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
    roles: ["Security Analyst", "SOC Engineer", "Security Manager", "Administrator", "analyst", "soc", "manager", "admin"],
  },
  {
    name: "Threat Center",
    path: "/threats",
    icon: TriangleAlert,
    roles: ["Security Analyst", "SOC Engineer", "Administrator", "analyst", "soc", "admin"],
  },
  {
    name: "Employees",
    path: "/employees",
    icon: Users,
    roles: ["Security Analyst", "SOC Engineer", "Administrator", "analyst", "soc", "admin"],
  },
  {
    name: "Employee Evaluation",
    path: "/employee-evaluation",
    icon: UserPlus,
    roles: ["Security Analyst", "SOC Engineer", "Security Manager", "Administrator", "analyst", "soc", "manager", "admin"],
  },
  {
    name: "Investigation",
    path: "/investigation",
    icon: Search,
    roles: ["Security Analyst", "SOC Engineer", "Administrator", "analyst", "soc", "admin"],
  },
  {
    name: "Reports",
    path: "/reports",
    icon: FileText,
    roles: ["Security Analyst", "SOC Engineer", "Security Manager", "Administrator", "analyst", "soc", "manager", "admin"],
  },
];

export default function Sidebar() {
  const { user } = useAuth();
  const userRole = user?.role || "Security Analyst";

  const menuItems = allMenuItems.filter((item) => {
    if (!item.roles) return true;
    return item.roles.some((r) => r.toLowerCase() === userRole.toLowerCase());
  });

  return (
    <aside
      className="
        relative
        z-20
        flex
        h-full
        w-[230px]
        min-w-[230px]
        shrink-0
        flex-col
        overflow-hidden
        border-r
        border-slate-800/80
        bg-slate-950/90
        backdrop-blur-xl
      "
    >
      {/* BRAND */}
      <div
        className="
          flex
          h-[70px]
          shrink-0
          items-center
          border-b
          border-slate-800/80
          px-4
        "
      >
        <Link
          to="/dashboard"
          aria-label="Go to SentinelAI home"
          className="
            group
            flex
            w-full
            min-w-0
            items-center
            gap-3
            rounded-xl
            p-1.5
            transition-all
            duration-200
            hover:bg-cyan-500/10
            focus:outline-none
            focus:ring-2
            focus:ring-cyan-500/40
          "
        >
          <div
            className="
              flex
              h-9
              w-9
              shrink-0
              items-center
              justify-center
              rounded-xl
              bg-gradient-to-br
              from-cyan-400
              to-blue-600
              shadow-md
              shadow-cyan-500/20
              transition-transform
              duration-200
              group-hover:scale-105
            "
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-5 w-5 text-white"
            >
              <path
                d="M12 3L19 6V11.5C19 16.3 16.1 20.4 12 21C7.9 20.4 5 16.3 5 11.5V6L12 3Z"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinejoin="round"
              />
              <path
                d="M9 12L11 14L15 10"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          <div className="min-w-0">
            <h1 className="whitespace-nowrap text-lg font-bold tracking-tight text-white transition-colors duration-200 group-hover:text-cyan-300">
              SentinelAI
            </h1>
            <p className="whitespace-nowrap text-[11px] text-slate-400">
              Insider Threat Platform
            </p>
          </div>
        </Link>
      </div>

      {/* NAVIGATION */}
      <nav
        className="
          min-h-0
          flex-1
          overflow-y-auto
          px-3
          py-3
          scrollbar-thin
          scrollbar-thumb-cyan-500/20
          scrollbar-track-transparent
        "
      >
        <div className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `
                    group
                    flex
                    h-9
                    w-full
                    items-center
                    gap-2.5
                    rounded-xl
                    border
                    px-3
                    py-1.5
                    transition-all
                    duration-200
                    ${
                      isActive
                        ? `
                          border-cyan-400/25
                          bg-cyan-500/15
                          text-cyan-300
                          shadow-md
                          shadow-cyan-500/10
                        `
                        : `
                          border-transparent
                          text-slate-300
                          hover:border-cyan-500/10
                          hover:bg-cyan-500/10
                          hover:text-cyan-300
                        `
                    }
                  `
                }
              >
                <Icon
                  size={17}
                  strokeWidth={1.8}
                  className="
                    shrink-0
                    transition-transform
                    duration-200
                    group-hover:scale-105
                  "
                />

                <span className="truncate text-xs font-semibold">
                  {item.name}
                </span>
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* SECURITY STATUS */}
      <div
        className="
          shrink-0
          border-t
          border-slate-800/80
          p-3
        "
      >
        <div
          className="
            rounded-xl
            border
            border-cyan-500/20
            bg-gradient-to-r
            from-cyan-500/10
            to-blue-500/10
            p-3
          "
        >
          <p className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
            Security Status
          </p>

          <div className="mt-1 flex items-center gap-2">
            <span
              className="
                h-2
                w-2
                shrink-0
                rounded-full
                bg-emerald-400
                shadow-sm
                shadow-emerald-500/50
                animate-pulse
              "
            />

            <span className="text-xs font-bold text-emerald-400">
              System Protected
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
