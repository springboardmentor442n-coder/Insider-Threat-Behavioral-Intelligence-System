import { motion } from "framer-motion";

export default function FeatureImportanceTable({
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
          Feature Importance
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Statistical characteristics of the behavioral
          features used by the intelligence pipeline.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left">
          <thead>
            <tr className="border-b border-slate-700 text-sm text-slate-400">
              <th className="px-4 py-3">
                Feature
              </th>

              <th className="px-4 py-3">
                Mean
              </th>

              <th className="px-4 py-3">
                Median
              </th>

              <th className="px-4 py-3">
                Minimum
              </th>

              <th className="px-4 py-3">
                Maximum
              </th>

              <th className="px-4 py-3">
                Std. Deviation
              </th>

              <th className="px-4 py-3">
                CV
              </th>
            </tr>
          </thead>

          <tbody>
            {data.map((item, index) => (
              <motion.tr
                key={`${item.Feature}-${index}`}
                initial={{
                  opacity: 0,
                }}
                animate={{
                  opacity: 1,
                }}
                transition={{
                  delay: index * 0.02,
                }}
                className="
                  border-b
                  border-slate-800
                  transition
                  hover:bg-slate-800/50
                "
              >
                <td className="px-4 py-3 font-medium text-cyan-300">
                  {item.Feature}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(item.Mean).toFixed(3)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(item.Median).toFixed(3)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(item.Minimum).toFixed(3)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(item.Maximum).toFixed(3)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(
                    item["Standard Deviation"]
                  ).toFixed(3)}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {Number(
                    item["Coefficient of Variation"]
                  ).toFixed(3)}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
