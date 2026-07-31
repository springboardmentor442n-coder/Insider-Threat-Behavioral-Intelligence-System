import { motion } from "framer-motion";

export default function StatCard({
  title,
  value,
  icon,
  color,
  subtitle = "Updated Today",
}) {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.02 }}
      transition={{ duration: 0.25 }}
      className="group rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg transition hover:border-cyan-500 hover:shadow-cyan-500/20"
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-sm uppercase tracking-wider text-slate-400">
            {title}
          </p>

          <h2 className="mt-3 text-4xl font-bold text-white">
            {value}
          </h2>

          <p className="mt-3 text-sm text-green-400">
            ▲ {subtitle}
          </p>

        </div>

        <div
          className="flex h-16 w-16 items-center justify-center rounded-2xl"
          style={{
            backgroundColor: `${color}25`,
          }}
        >
          {icon}
        </div>

      </div>
    </motion.div>
  );
}