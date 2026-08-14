import { motion } from "framer-motion";

export default function MetricCard({
  title,
  value,
  icon: Icon,
  color = "text-cyan-400",
  bgColor = "bg-cyan-500/10",
  borderColor = "border-cyan-500/20",
  subtitle,
}) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      className={`relative overflow-hidden rounded-2xl border ${borderColor || "border-slate-800/80"} bg-slate-900/60 p-5 backdrop-blur-xl shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {title}
          </p>

          <h2 className={`mt-2 text-3xl font-extrabold ${color}`}>
            {value}
          </h2>

          {subtitle && (
            <p className="mt-1 text-xs text-slate-500">
              {subtitle}
            </p>
          )}
        </div>

        {Icon && (
          <div className={`flex h-11 w-11 items-center justify-center rounded-xl border ${borderColor || "border-white/10"} ${bgColor || "bg-white/5"}`}>
            <Icon size={22} className={color} />
          </div>
        )}
      </div>
    </motion.div>
  );
}
