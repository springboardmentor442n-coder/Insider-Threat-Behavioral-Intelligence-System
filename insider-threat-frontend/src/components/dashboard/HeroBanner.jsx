import { ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function HeroBanner() {
  return (
    <motion.section
      initial={{ opacity: 0, y: -25 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 p-8 shadow-lg"
    >
      <div className="flex items-center gap-4">
        <div className="rounded-xl bg-cyan-500/10 p-4">
          <ShieldCheck className="h-10 w-10 text-cyan-400" />
        </div>

        <div>
          <h1 className="text-4xl font-bold text-white">
            SentinelAI Dashboard
          </h1>

          <p className="mt-2 text-slate-400">
            Insider Threat Behavioral Intelligence System
          </p>
        </div>
      </div>
    </motion.section>
  );
}
