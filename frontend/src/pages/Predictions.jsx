import { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  Search,
  ShieldAlert,
  ShieldCheck,
  Brain,
} from "lucide-react";

import Layout from "../components/Layout";

export default function Predictions() {

  const [predictions, setPredictions] = useState([]);
  const [filtered, setFiltered] = useState([]);

  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");

  useEffect(() => {
    loadPredictions();
  }, []);

  async function loadPredictions() {

    try {

      const res = await axios.get(
        "http://127.0.0.1:8000/predictions"
      );

      setPredictions(res.data);
      setFiltered(res.data);

    } catch (err) {

      console.error(err);

    }

  }

  useEffect(() => {

    let data = [...predictions];

    if (search !== "") {

      data = data.filter((item) =>
        item.employee_id
          ?.toLowerCase()
          .includes(search.toLowerCase())
      );

    }

    if (riskFilter !== "ALL") {

      data = data.filter(
        (item) => item.risk_level === riskFilter
      );

    }

    setFiltered(data);

  }, [search, riskFilter, predictions]);

  const total = predictions.length;

  const highRisk = predictions.filter(
    (p) => p.risk_level === "HIGH"
  ).length;

  const lowRisk = predictions.filter(
    (p) => p.risk_level === "LOW"
  ).length;

  return (

    <Layout title="AI Threat Predictions">

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >

        <h2 className="text-4xl font-bold text-white">

          AI Threat Predictions

        </h2>

        <p className="mt-2 text-slate-400">

          View and analyse insider threat predictions.

        </p>

      </motion.div>

      {/* Statistics */}

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <Brain className="text-cyan-400"/>

            <span className="text-slate-400">

              Total Predictions

            </span>

          </div>

          <h2 className="mt-5 text-4xl font-bold text-cyan-400">

            {total}

          </h2>

        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <ShieldAlert className="text-red-400"/>

            <span className="text-slate-400">

              High Risk

            </span>

          </div>

          <h2 className="mt-5 text-4xl font-bold text-red-400">

            {highRisk}

          </h2>

        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <ShieldCheck className="text-green-400"/>

            <span className="text-slate-400">

              Low Risk

            </span>

          </div>

          <h2 className="mt-5 text-4xl font-bold text-green-400">

            {lowRisk}

          </h2>

        </div>

      </div>

      {/* Search */}

      <div className="mt-8 flex flex-col gap-4 md:flex-row md:justify-between">

        <div className="relative w-full md:w-96">

          <Search
            size={18}
            className="absolute left-4 top-3.5 text-slate-400"
          />

          <input
            type="text"
            placeholder="Search Employee..."
            value={search}
            onChange={(e)=>setSearch(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-900 py-3 pl-11 pr-4 text-white outline-none focus:border-cyan-400"
          />

        </div>

        <select
          value={riskFilter}
          onChange={(e)=>setRiskFilter(e.target.value)}
          className="rounded-xl border border-slate-700 bg-slate-900 px-5 py-3 text-white outline-none"
        >

          <option value="ALL">

            All Risks

          </option>

          <option value="HIGH">

            High Risk

          </option>

          <option value="LOW">

            Low Risk

          </option>

        </select>

      </div>

      <motion.div
        initial={{opacity:0}}
        animate={{opacity:1}}
        transition={{delay:.3}}
        className="mt-8 overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-xl"
      >

        <table className="w-full">

          <thead className="bg-slate-800 text-slate-300">

            <tr>

              <th className="px-6 py-4 text-left">

                Employee

              </th>

              <th className="px-6 py-4 text-left">

                Department

              </th>

              <th className="px-6 py-4 text-left">

                Login

              </th>

              <th className="px-6 py-4 text-left">

                Devices

              </th>

              <th className="px-6 py-4 text-left">

                Hour

              </th>

              <th className="px-6 py-4 text-left">

                Risk

              </th>

              <th className="px-6 py-4 text-left">

                Confidence

              </th>

            </tr>

          </thead>

          <tbody>
                        {filtered.length === 0 ? (

              <tr>

                <td
                  colSpan="7"
                  className="py-12 text-center text-slate-400"
                >
                  No predictions found.
                </td>

              </tr>

            ) : (

              filtered.map((item) => (

                <tr
                  key={item.prediction_id}
                  className="border-t border-slate-800 transition-all hover:bg-slate-800/40"
                >

                  <td className="px-6 py-4 font-medium text-cyan-400">
                    {item.employee_id}
                  </td>

                  <td className="px-6 py-4 text-white">
                    {item.department}
                  </td>

                  <td className="px-6 py-4 text-slate-300">
                    {item.login_count}
                  </td>

                  <td className="px-6 py-4 text-slate-300">
                    {item.unique_pc_count}
                  </td>

                  <td className="px-6 py-4 text-slate-300">
                    {item.hour}:00
                  </td>

                  <td className="px-6 py-4">

                    <span
                      className={`rounded-lg px-3 py-1 font-semibold ${
                        item.risk_level === "HIGH"
                          ? "bg-red-500/20 text-red-400"
                          : "bg-green-500/20 text-green-400"
                      }`}
                    >
                      {item.risk_level}
                    </span>

                  </td>

                  <td className="px-6 py-4">

                    <span className="rounded-lg bg-cyan-500/20 px-3 py-1 text-cyan-400">

                      {Number(item.confidence).toFixed(2)}%

                    </span>

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </motion.div>

    </Layout>

  );

}