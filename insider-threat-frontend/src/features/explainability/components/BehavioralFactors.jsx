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
        border border-slate-700
        bg-slate-900/60
        p-6
      "
    >
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-white">
          Top Behavioral Factors
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Highest-ranked behavioral activity observed
          in the generated intelligence report.
        </p>
      </div>

      <div className="space-y-3">
        {data.map((item, index) => {
          const Icon =
            icons[index % icons.length];

          return (
            <motion.div
              key={`${item.Rank}-${item.Behavior}`}
              initial={{
                opacity: 0,
                x: -10,
              }}
              animate={{
                opacity: 1,
                x: 0,
              }}
              transition={{
                delay: index * 0.05,
              }}
              className="
                flex
                items-center
                gap-4
                rounded-xl
                border
                border-slate-700
                bg-slate-800/40
                p-4
              "
            >
              <div
                className="
                  flex
                  h-11
                  w-11
                  shrink-0
                  items-center
                  justify-center
                  rounded-xl
                  bg-cyan-500/10
                "
              >
                <Icon
                  size={20}
                  className="text-cyan-400"
                />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500">
                    #{item.Rank}
                  </span>

                  <p className="font-semibold text-white">
                    {item.Behavior}
                  </p>
                </div>

                <p className="mt-1 text-sm text-slate-400">
                  Average:{" "}
                  {Number(
                    item["Average Value"]
                  ).toFixed(2)}
                </p>
              </div>

              <div className="text-right">
                <p className="text-xs text-slate-500">
                  Maximum
                </p>

                <p className="font-semibold text-orange-400">
                  {Number(
                    item["Maximum Value"]
                  ).toFixed(2)}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
