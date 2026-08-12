import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import TopNavbar from "../components/layout/TopNavbar";
import AnimatedBackground from "../components/common/AnimatedBackground";

import "../styles/glass.css";

export default function AppShell() {
  return (
    <div
      className="
        relative
        flex
        h-screen
        w-full
        min-w-0
        overflow-hidden
        bg-slate-950
        text-slate-100
      "
    >
      {/* =====================================================
          GLOBAL BACKGROUND
          ===================================================== */}

      <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
        <AnimatedBackground />
      </div>

      {/* =====================================================
          APPLICATION LAYOUT
          ===================================================== */}

      <div
        className="
          relative
          z-10

          flex
          h-full
          w-full
          min-w-0

          overflow-hidden
        "
      >
        {/* ===================================================
            SIDEBAR
            =================================================== */}

        <Sidebar />

        {/* ===================================================
            MAIN AREA
            =================================================== */}

        <div
          className="
            flex
            h-full
            min-w-0
            flex-1
            flex-col
            overflow-hidden
          "
        >
          {/* TOP NAVBAR */}

          <TopNavbar />

          {/* PAGE AREA */}
          <main
            className="
              min-h-0
              min-w-0
              flex-1
              overflow-y-auto
              overflow-x-hidden
              p-4
              sm:p-5
              lg:p-6
              scrollbar-thin
              scrollbar-thumb-cyan-500/30
              scrollbar-track-transparent
            "
          >
            <div
              className="
                mx-auto
                w-full
                max-w-[1600px]
              "
            >
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
