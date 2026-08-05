import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar";
import TopNavbar from "../components/layout/TopNavbar";

import "../styles/glass.css";

export default function AppShell() {
  return (
    <div
      className="
        relative

        flex

        h-screen

        overflow-hidden

        bg-[#050816]

        text-white
      "
    >
      {/* ====================================================== */}
      {/* Premium Animated Cyber Background */}
      {/* ====================================================== */}

      <div className="fixed inset-0 -z-20 overflow-hidden">

        {/* Cyan Glow */}
        <div
          className="
            absolute

            -left-80
            -top-80

            h-[900px]
            w-[900px]

            rounded-full

            bg-cyan-500/10

            blur-[240px]

            animate-pulse
          "
        />

        {/* Blue Glow */}
        <div
          className="
            absolute

            -right-80
            -bottom-80

            h-[750px]
            w-[750px]

            rounded-full

            bg-blue-500/10

            blur-[220px]

            animate-pulse
          "
          style={{
            animationDelay: "2s",
          }}
        />

        {/* Purple Glow */}
        <div
          className="
            absolute

            left-1/2
            top-1/2

            h-[500px]
            w-[500px]

            -translate-x-1/2
            -translate-y-1/2

            rounded-full

            bg-purple-500/10

            blur-[220px]

            animate-pulse
          "
          style={{
            animationDelay: "4s",
          }}
        />

        {/* Small Cyan Orb */}
        <div
          className="
            absolute

            top-24
            right-40

            h-32
            w-32

            rounded-full

            bg-cyan-400/10

            blur-[90px]
          "
        />

        {/* Small Blue Orb */}
        <div
          className="
            absolute

            bottom-32
            left-44

            h-40
            w-40

            rounded-full

            bg-blue-400/10

            blur-[100px]
          "
        />

      </div>

      {/* ====================================================== */}
      {/* Subtle Grid Overlay */}
      {/* ====================================================== */}

      <div
        className="
          pointer-events-none

          fixed

          inset-0

          -z-10

          opacity-[0.04]

          bg-[linear-gradient(rgba(255,255,255,.2)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.2)_1px,transparent_1px)]

          bg-[size:60px_60px]
        "
      />

      {/* ====================================================== */}
      {/* Sidebar */}
      {/* ====================================================== */}

      <Sidebar />

      {/* ====================================================== */}
      {/* Main Section */}
      {/* ====================================================== */}

      <div
        className="
          flex

          flex-1

          flex-col

          overflow-hidden
        "
      >
        {/* Navbar */}

        <TopNavbar />

        {/* ====================================================== */}
        {/* Main Content */}
        {/* ====================================================== */}

        <main
          className="
            flex-1

            overflow-y-auto

            px-8

            py-8

            bg-transparent

            scrollbar-thin

            scrollbar-thumb-cyan-500/40

            scrollbar-track-transparent
          "
        >
          <div
            className="
              mx-auto

              w-full

              max-w-[1700px]
            "
          >
            <Outlet />
          </div>
        </main>

      </div>

    </div>
  );
}
