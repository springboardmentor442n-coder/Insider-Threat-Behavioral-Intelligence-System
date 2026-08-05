import { NavLink } from "react-router-dom";
import {
  Shield,
  LayoutDashboard,
  TriangleAlert,
  Users,
  BarChart3,
  FileText,
  Settings,
} from "lucide-react";

const menuItems = [
  {
    name: "Dashboard",
    path: "/",
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
      glass-card
      m-4
      w-72
      rounded-3xl
      border
      border-cyan-500/20
      overflow-hidden
      flex
      flex-col
      shadow-2xl
    "
    >
      {/* ========================= */}
      {/* Logo */}
      {/* ========================= */}

      <div className="border-b border-white/10 p-8">

        <div className="flex items-center gap-4">

          <div
            className="
            flex
            h-14
            w-14
            items-center
            justify-center

            rounded-2xl

            bg-gradient-to-br
            from-cyan-500
            via-sky-500
            to-blue-600

            shadow-lg
            shadow-cyan-500/30
          "
          >
            <Shield
              size={30}
              className="text-white"
            />
          </div>

          <div>

            <h1 className="text-2xl font-bold tracking-wide">
              SentinelAI
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              Insider Threat Platform
            </p>

          </div>

        </div>

      </div>

      {/* ========================= */}
      {/* Navigation */}
      {/* ========================= */}

      <nav className="flex-1 px-4 py-6 space-y-2">

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.name}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `
                group
                flex
                items-center
                gap-4

                rounded-2xl

                px-5
                py-4

                transition-all
                duration-300

                ${
                  isActive
                    ? `
                      bg-cyan-500/20
                      border
                      border-cyan-400/30

                      text-cyan-300

                      shadow-lg
                      shadow-cyan-500/20
                    `
                    : `
                      text-slate-300

                      hover:bg-cyan-500/10
                      hover:text-cyan-300
                      hover:translate-x-1
                    `
                }
              `
              }
            >
              <Icon
                size={20}
                className="
                transition-transform
                duration-300
                group-hover:scale-110
              "
              />

              <span className="font-medium tracking-wide">
                {item.name}
              </span>
            </NavLink>
          );
        })}

      </nav>

      {/* ========================= */}
      {/* Footer */}
      {/* ========================= */}

      <div
        className="
        border-t
        border-white/10

        p-5
      "
      >

        <div
          className="
          rounded-2xl

          bg-gradient-to-r
          from-cyan-500/10
          to-blue-500/10

          border
          border-cyan-500/20

          p-4
        "
        >

          <p className="text-xs text-slate-400">
            Security Status
          </p>

          <div className="mt-2 flex items-center gap-2">

            <div
              className="
              h-3
              w-3

              rounded-full

              bg-green-500

              animate-pulse
            "
            />

            <span className="font-semibold text-green-400">
              System Protected
            </span>

          </div>

        </div>

      </div>

    </aside>
  );
}
