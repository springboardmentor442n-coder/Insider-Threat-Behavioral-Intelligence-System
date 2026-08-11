import { motion } from "framer-motion";

export default function AnimatedBackground() {
  return (
    <div
      className="
        pointer-events-none
        fixed
        inset-0
        -z-50
        overflow-hidden
        bg-[#020617]
      "
      aria-hidden="true"
    >
      {/* =========================================================
          CENTRAL CYAN GLOW
          Matches the LoginPage visual language
          ========================================================= */}
      <motion.div
        className="
          absolute
          left-1/2
          top-1/2
          h-[520px]
          w-[520px]
          -translate-x-1/2
          -translate-y-1/2
          rounded-full
          bg-cyan-500/10
          blur-[120px]
        "
        animate={{
          scale: [1, 1.12, 1],
          opacity: [0.55, 0.8, 0.55],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* =========================================================
          TOP LEFT BLUE GLOW
          ========================================================= */}
      <motion.div
        className="
          absolute
          left-[8%]
          top-[12%]
          h-52
          w-52
          rounded-full
          bg-blue-600/10
          blur-[100px]
        "
        animate={{
          x: [0, 35, 0],
          y: [0, 25, 0],
          scale: [1, 1.08, 1],
          opacity: [0.45, 0.7, 0.45],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* =========================================================
          BOTTOM RIGHT CYAN GLOW
          ========================================================= */}
      <motion.div
        className="
          absolute
          bottom-[8%]
          right-[8%]
          h-60
          w-60
          rounded-full
          bg-cyan-400/10
          blur-[110px]
        "
        animate={{
          x: [0, -30, 0],
          y: [0, -20, 0],
          scale: [1, 1.1, 1],
          opacity: [0.4, 0.65, 0.4],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* =========================================================
          PURPLE ACCENT
          ========================================================= */}
      <motion.div
        className="
          absolute
          left-[45%]
          top-[25%]
          h-72
          w-72
          rounded-full
          bg-purple-500/[0.035]
          blur-[130px]
        "
        animate={{
          x: [0, 45, -20, 0],
          y: [0, -25, 30, 0],
          scale: [1, 1.08, 0.96, 1],
        }}
        transition={{
          duration: 16,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* =========================================================
          SUBTLE CYBER GRID
          Same visual language as LoginPage
          ========================================================= */}
      <div
        className="
          absolute
          inset-0
          opacity-[0.035]
        "
        style={{
          backgroundImage:
            "linear-gradient(rgba(148,163,184,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.5) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* =========================================================
          VERY SUBTLE VIGNETTE
          ========================================================= */}
      <div
        className="
          absolute
          inset-0
          bg-[radial-gradient(circle_at_center,transparent_20%,rgba(2,6,23,0.35)_100%)]
        "
      />
    </div>
  );
}
