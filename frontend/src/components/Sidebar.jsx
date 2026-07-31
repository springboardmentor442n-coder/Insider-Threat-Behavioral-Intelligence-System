import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  ShieldAlert,
  BarChart3,
  Cpu,
  LogOut,
  Shield,
} from "lucide-react";

export default function Sidebar() {
  const menuItems = [
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: <LayoutDashboard size={20} />,
    },
    {
      name: "Employees",
      path: "/employees",
      icon: <Users size={20} />,
    },
    {
      name: "Predictions",
      path: "/predictions",
      icon: <ShieldAlert size={20} />,
    },
    {
      name: "Analytics",
      path: "/analytics",
      icon: <BarChart3 size={20} />,
    },
    {
      name: "Pipeline",
      path: "/pipeline",
      icon: <Cpu size={20} />,
    },
  ];

  return (
    <aside className="flex h-screen w-72 flex-col border-r border-slate-800 bg-slate-950 shadow-2xl">

      {/* Logo */}

      <div className="border-b border-slate-800 p-8">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-cyan-500 p-3">

            <Shield size={28} className="text-white" />

          </div>

          <div>

            <h1 className="text-2xl font-bold text-cyan-400">
              ThreatGuard
            </h1>

            <p className="text-sm text-slate-400">
              AI Security Platform
            </p>

          </div>

        </div>

      </div>

      {/* Navigation */}

      <div className="flex-1 p-5">

        <p className="mb-5 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Navigation
        </p>

        <div className="space-y-2">

          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-4 rounded-xl px-4 py-4 transition-all duration-300 ${
                  isActive
                    ? "bg-cyan-500 text-white shadow-lg"
                    : "text-slate-300 hover:bg-slate-800 hover:text-cyan-400"
                }`
              }
            >
              {item.icon}

              <span className="font-medium">
                {item.name}
              </span>
            </NavLink>
          ))}

        </div>

      </div>

      {/* Footer */}

      <div className="border-t border-slate-800 p-6">

        <div className="mb-5 rounded-xl bg-slate-900 p-4">

          <p className="text-sm text-slate-400">
            Logged in as
          </p>

          <p className="mt-1 font-semibold text-white">
            Administrator
          </p>

        </div>

        <button
          className="flex w-full items-center justify-center gap-3 rounded-xl bg-red-500 px-4 py-3 font-semibold text-white transition hover:bg-red-600"
          onClick={() => {
            localStorage.removeItem("token");
            window.location.href = "/login";
          }}
        >
          <LogOut size={18} />
          Logout
        </button>

      </div>

    </aside>
  );
}