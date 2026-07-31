import { motion } from "framer-motion";
import { ShieldCheck, Brain, Activity, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-white">

      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900"></div>

      {/* Animated Blur */}
      <div className="absolute -top-20 -left-20 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl animate-pulse"></div>

      <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-blue-700/20 blur-3xl animate-pulse"></div>

      {/* Navbar */}

      <nav className="relative z-10 flex items-center justify-between px-10 py-6">

        <h1 className="text-2xl font-bold tracking-wide text-cyan-400">
          ThreatGuard AI
        </h1>

        <Link
          to="/login"
          className="rounded-lg bg-cyan-500 px-6 py-2 font-semibold transition hover:bg-cyan-400"
        >
          Login
        </Link>

      </nav>

      {/* Hero */}

<div className="relative z-10 flex min-h-[60vh] items-center justify-center px-10">
  <div className="max-w-4xl text-center">

    <motion.h1
      initial={{ opacity: 0, y: -40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
      className="mb-6 text-6xl font-extrabold leading-tight"
    >
      AI-Powered
      <span className="text-cyan-400"> Insider Threat </span>
      Behavioral Intelligence System
    </motion.h1>

    <motion.p
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="mx-auto max-w-3xl text-lg text-slate-300"
    >
      Detect potential insider threats by analyzing employee behavioral
      patterns using engineered behavioral features and a Random Forest
      machine learning model trained on the CERT Insider Threat Dataset v4.2.
    </motion.p>

    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1 }}
      className="mt-8 flex justify-center"
    >
      <Link
        to="/login"
        className="flex items-center gap-2 rounded-xl bg-cyan-500 px-8 py-4 text-lg font-semibold transition hover:scale-105 hover:bg-cyan-400"
      >
        Launch Platform
        <ArrowRight size={22} />
      </Link>
    </motion.div>

  </div>
</div>

      {/* Features */}

      <div className="relative z-10 mx-auto mb-20 grid max-w-7xl grid-cols-1 gap-8 px-10 md:grid-cols-3">

        <motion.div
          whileHover={{ scale:1.05 }}
          className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
        >
          <ShieldCheck className="mb-5 text-cyan-400" size={45}/>
          <h2 className="mb-4 text-2xl font-bold">
            Insider Threat Detection
          </h2>
          <p className="text-slate-400">
            Identify suspicious employee activities before they become security incidents.
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale:1.05 }}
          className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
        >
          <Brain className="mb-5 text-cyan-400" size={45}/>
          <h2 className="mb-4 text-2xl font-bold">
            Explainable AI
          </h2>
          <p className="text-slate-400">
            Every prediction includes confidence scores and risk explanations.
          </p>
        </motion.div>

        <motion.div
          whileHover={{ scale:1.05 }}
          className="rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
        >
          <Activity className="mb-5 text-cyan-400" size={45}/>
          <h2 className="mb-4 text-2xl font-bold">
            Behavioral Analytics
          </h2>
          <p className="text-slate-400">
            Analyze logon, email, HTTP, device and file activity using AI.
          </p>
        </motion.div>

      </div>

    </div>
  );
}