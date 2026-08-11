import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  TriangleAlert,
  Users,
  BarChart3,
  BrainCircuit,
  Sparkles,
  Search,
  FileText,
  Settings,
} from "lucide-react";

const menuItems = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Threat Center",
    path: "/threats",
    icon: TriangleAlert,
  },
  {
    name: "Employees",
    path: "/employees",
    icon: Users,
  },
  {
    name: "Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Models",
    path: "/models",
    icon: BrainCircuit,
  },
  {
    name: "Explainability",
    path: "/explainability",
    icon: Sparkles,
  },
  {
    name: "Investigation",
    path: "/investigation",
    icon: Search,
  },
  {
    name: "Reports",
    path: "/reports",
    icon: FileText,
  },
  {
    name: "Settings",
    path: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside
      className="
        relative
        z-20

        flex
        h-full
        w-[264px]
        min-w-[264px]
        shrink-0
        flex-col

        overflow-hidden

        border-r
        border-white/10

        bg-slate-950/90

        backdrop-blur-xl
      "
    >
      {/* =====================================================
          BRAND
          ===================================================== */}

      <div
        className="
          flex
          h-[136px]
          shrink-0
          items-center

          border-b
          border-white/10

          px-7
        "
      >
        <div className="flex min-w-0 items-center gap-4">
          <div
            className="
              flex
              h-16
              w-16
              shrink-0
              items-center
              justify-center

              rounded-2xl

              bg-gradient-to-br
              from-cyan-400
              to-blue-600

              shadow-lg
              shadow-cyan-500/25
            "
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-9 w-9 text-white"
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
            <h1 className="whitespace-nowrap text-[24px] font-bold tracking-tight text-white">
              SentinelAI
            </h1>

            <p className="mt-0.5 whitespace-nowrap text-[13px] text-slate-400">
              Insider Threat Platform
            </p>
          </div>
        </div>
      </div>

      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <nav
        className="
          min-h-0
          flex-1
          overflow-y-auto

          px-4
          py-5

          scrollbar-thin
          scrollbar-thumb-cyan-500/20
          scrollbar-track-transparent
        "
      >
        <div className="space-y-1.5">
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
                    min-h-[50px]
                    w-full
                    items-center
                    gap-3.5

                    rounded-2xl

                    border

                    px-4
                    py-3

                    transition-all
                    duration-200

                    ${
                      isActive
                        ? `
                          border-cyan-400/25
                          bg-cyan-500/15
                          text-cyan-300
                          shadow-lg
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
                  size={21}
                  strokeWidth={1.9}
                  className="
                    shrink-0
                    transition-transform
                    duration-200
                    group-hover:scale-105
                  "
                />

                <span className="truncate text-[15px] font-medium">
                  {item.name}
                </span>
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* =====================================================
          SECURITY STATUS
          ===================================================== */}

      <div
        className="
          shrink-0
          border-t
          border-white/10
          p-4
        "
      >
        <div
          className="
            rounded-2xl
            border
            border-cyan-500/20

            bg-gradient-to-r
            from-cyan-500/10
            to-blue-500/10

            px-4
            py-3.5
          "
        >
          <p className="text-[11px] text-slate-400">
            Security Status
          </p>

          <div className="mt-2 flex items-center gap-2">
            <span
              className="
                h-2.5
                w-2.5
                shrink-0
                rounded-full

                bg-emerald-500

                shadow-sm
                shadow-emerald-500/50

                animate-pulse
              "
            />

            <span className="text-sm font-semibold text-emerald-400">
              System Protected
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
