import { motion } from "framer-motion";
import AnimatedCounter from "./AnimatedCounter";
import GlassCard from "./GlassCard";

export default function MetricCard({
  title,
  value,
  subtitle,
  color = "text-cyan-400",
  icon: Icon,
}) {
  return (
    <motion.div
      whileHover={{
        y: -6,
        scale: 1.02,
      }}
      transition={{
        duration: 0.25,
      }}
    >
      <GlassCard className="relative overflow-hidden p-6">

        {/* Background Glow */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-500/5" />

        <div className="relative z-10">

          <div className="flex items-center justify-between">

            <p className="text-sm font-medium text-slate-400">
              {title}
            </p>

            {Icon && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-2">
                <Icon
                  size={20}
                  className={color}
                />
              </div>
            )}

          </div>

          <div className={`mt-5 text-4xl font-bold ${color}`}>

            {typeof value === "number" ? (
              <AnimatedCounter value={value} />
            ) : (
              value
            )}

          </div>

          <p className="mt-3 text-sm text-slate-500">
            {subtitle}
          </p>

        </div>

      </GlassCard>
    </motion.div>
  );
}
