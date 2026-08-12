import { motion } from "framer-motion";
import { formatFeatureName, formatNumber } from "../../../utils/formatters";

export default function FeatureImportanceTable({
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
          Feature Importance & Statistical Metrics
        </h2>

        <p className="mt-0.5 text-xs text-slate-400">
          Statistical characteristics of the behavioral features used by the unsupervised ML intelligence pipeline.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[11px]">
              <th className="px-4 py-3">Feature Name</th>
              <th className="px-4 py-3">Mean</th>
              <th className="px-4 py-3">Median</th>
              <th className="px-4 py-3">Minimum</th>
              <th className="px-4 py-3">Maximum</th>
              <th className="px-4 py-3">Std. Deviation</th>
              <th className="px-4 py-3">CV</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/60 font-mono">
            {data.map((item, index) => (
              <motion.tr
                key={`${item.Feature}-${index}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.02 }}
                className="transition hover:bg-slate-800/40"
              >
                <td className="px-4 py-3 font-sans font-bold text-cyan-300">
                  {formatFeatureName(item.Feature)}
                </td>

                <td className="px-4 py-3 text-slate-200">
                  {formatNumber(item.Mean, 2)}
                </td>

                <td className="px-4 py-3 text-slate-200">
                  {formatNumber(item.Median, 2)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {formatNumber(item.Minimum, 2)}
                </td>

                <td className="px-4 py-3 text-orange-400 font-bold">
                  {formatNumber(item.Maximum, 2)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {formatNumber(item["Standard Deviation"], 2)}
                </td>

                <td className="px-4 py-3 text-purple-400 font-bold">
                  {formatNumber(item["Coefficient of Variation"], 2)}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
