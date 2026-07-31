import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Settings,
  LogOut,
  ChevronDown,
} from "lucide-react";


export default function Layout({ title, children }) {
    const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);

  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () =>
      document.removeEventListener(
        "mousedown",
        handleClickOutside
      );
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");

    navigate("/login");
  };
  return (
  <div className="min-h-screen bg-slate-950 text-white">

    {/* ================= TOP NAVBAR ================= */}

    <motion.header
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-lg"
    >
      <div className="flex h-20 items-center justify-between px-8">

        {/* Left */}

        <div>

          <h1 className="text-3xl font-bold text-cyan-400">
            {title}
          </h1>

          <p className="text-sm text-slate-400">
            AI Insider Threat Behavioural Intelligence System
          </p>

        </div>

        {/* Center Navigation */}

        <nav className="hidden md:flex items-center gap-8">

  <button
    onClick={() => navigate("/dashboard")}
    className="font-medium text-slate-300 transition hover:text-cyan-400"
  >
    Dashboard
  </button>

  <button
    onClick={() => navigate("/employees")}
    className="font-medium text-slate-300 transition hover:text-cyan-400"
  >
    Employees
  </button>

  <button
    onClick={() => navigate("/predictions")}
    className="font-medium text-slate-300 transition hover:text-cyan-400"
  >
    Predictions
  </button>

  <button
    onClick={() => navigate("/pipeline")}
    className="font-medium text-slate-300 transition hover:text-cyan-400"
  >
    Pipeline
  </button>

</nav>

        {/* Right */}

        <div
          className="relative"
          ref={menuRef}
        >

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-3 rounded-xl border border-slate-700 bg-slate-800 px-5 py-3 transition hover:border-cyan-500"
          >

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500">

              <User
                size={20}
                className="text-white"
              />

            </div>

            <div className="text-left">

              <p className="text-xs text-slate-400">
                Logged in as
              </p>

              <p className="font-semibold">
                Administrator
              </p>

            </div>

            <ChevronDown
              size={18}
              className={`transition ${
                menuOpen ? "rotate-180" : ""
              }`}
            />

          </button>

          <AnimatePresence>

            {menuOpen && (

              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 mt-3 w-64 rounded-xl border border-slate-700 bg-slate-900 shadow-2xl"
              >

                <div className="border-b border-slate-700 p-4">

                  <p className="font-semibold">
                    Administrator
                  </p>

                  <p className="text-sm text-slate-400">
                    AI Security Admin
                  </p>

                </div>

                <button
                  onClick={logout}
                  className="flex w-full items-center gap-3 px-5 py-4 text-red-400 transition hover:bg-red-500/10"
                >

                  <LogOut size={18} />

                  Logout

                </button>

              </motion.div>

            )}

          </AnimatePresence>

        </div>

      </div>

    </motion.header>

    {/* ================= PAGE ================= */}

    <motion.main
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="p-8"
    >

      {children}

    </motion.main>

  </div>
);
}