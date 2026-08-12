import { motion } from "framer-motion";
import {
  Activity,
  Clock,
  Database,
  FileWarning,
  Globe,
  HardDrive,
  CalendarDays,
} from "lucide-react";
import { formatFeatureName, formatNumber } from "../../../utils/formatters";

const icons = [
  Activity,
  Globe,
  CalendarDays,
  Clock,
  HardDrive,
  FileWarning,
  Database,
];

export default function BehavioralFactors({
  data = [],
}) {
  return (
    <section
      className="
        rounded-2xl
        border border-slate-800
        bg-slate-900/60
        p-5
        backdrop-blur-sm
      "
    >
      <div className="mb-4">
        <h2 className="text-lg font-bold text-white">
          Top Behavioral Factors
        </h2>

        <p className="mt-0.5 text-xs text-slate-400">
          Highest-ranked behavioral activity observed in the generated intelligence report.
        </p>
      </div>

      <div className="space-y-3">
        {data.map((item, index) => {
          const Icon = icons[index % icons.length];
          const formattedBehavior = formatFeatureName(item.Behavior);
          const formattedAverage = formatNumber(item["Average Value"]);
          const formattedMaximum = formatNumber(item["Maximum Value"]);

          return (
            <motion.div
              key={`${item.Rank}-${item.Behavior}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.04 }}
              className="
                flex
                items-center
                gap-4
                rounded-xl
                border
                border-slate-800
                bg-slate-950/40
                p-3.5
              "
            >
              <div
                className="
                  flex
                  h-10
                  w-10
                  shrink-0
                  items-center
                  justify-center
                  rounded-xl
                  border
                  border-cyan-500/20
                  bg-cyan-500/10
                "
              >
                <Icon size={18} className="text-cyan-400" />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-500">
                    #{item.Rank}
                  </span>

                  <p className="text-sm font-bold text-white truncate">
                    {formattedBehavior}
                  </p>
                </div>

                <p className="mt-0.5 text-xs text-slate-400">
                  Average: <span className="font-mono font-bold text-slate-200">{formattedAverage}</span>
                </p>
              </div>

              <div className="text-right shrink-0">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Maximum
                </p>

                <p className="font-mono text-sm font-bold text-orange-400">
                  {formattedMaximum}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
