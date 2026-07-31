import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { motion } from "framer-motion";
import {
  User,
  Building2,
  Mail,
  Briefcase,
  ShieldAlert,
  Activity,
} from "lucide-react";

import Layout from "../components/Layout";
function FeatureRow({ label, value }) {
  return (
    <div className="mb-3 flex justify-between border-b border-slate-800 pb-2">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold text-white">
        {value ?? 0}
      </span>
    </div>
  );
}
export default function EmployeeDetails() {

  const { employee_id } = useParams();

  const [data, setData] = useState(null);

  useEffect(() => {
    loadEmployee();
  }, [employee_id]);

  async function loadEmployee() {

    try {

      const res = await axios.get(
        `http://127.0.0.1:8000/behavior/${employee_id}`
      );

      setData(res.data);

    } catch (err) {

      console.error(err);

    }

  }

  if (!data) {

    return (
      <Layout title="Employee Profile">

        <div className="flex h-96 items-center justify-center">

          <h2 className="text-2xl font-semibold text-slate-300">
            Loading Employee...
          </h2>

        </div>

      </Layout>
    );

  }

  return (

    <Layout title="Employee Profile">

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >

        <h2 className="text-4xl font-bold text-white">

          {data.employee.name}

        </h2>

        <p className="mt-2 text-slate-400">

          AI Behavioural Intelligence Report

        </p>

      </motion.div>

      {/* Statistics */}

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <Activity className="text-cyan-400" />

            <span className="text-slate-400">

              Total Predictions

            </span>

          </div>

          <h2 className="mt-5 text-4xl font-bold text-cyan-400">

            {data.total_predictions}

          </h2>

        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <ShieldAlert className="text-red-400" />

            <span className="text-slate-400">

              High Risk Events

            </span>

          </div>

          <h2 className="mt-5 text-4xl font-bold text-red-400">

            {data.high_risk}

          </h2>

        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-center gap-3">

            <User className="text-green-400" />

            <span className="text-slate-400">

              Employee ID

            </span>

          </div>

          <h2 className="mt-5 text-2xl font-bold text-green-400">

            {data.employee.employee_id}

          </h2>

        </div>

      </div>

      {/* Employee Information */}

      <div className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-8">

        <h2 className="mb-6 text-2xl font-bold text-white">

          Employee Information

        </h2>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">

          <div className="flex items-center gap-4">

            <User className="text-cyan-400" />

            <div>

              <p className="text-slate-400">

                Name

              </p>

              <p className="font-semibold text-white">

                {data.employee.name}

              </p>

            </div>

          </div>

          <div className="flex items-center gap-4">

            <Building2 className="text-cyan-400" />

            <div>

              <p className="text-slate-400">

                Department

              </p>

              <p className="font-semibold text-white">

                {data.employee.department}

              </p>

            </div>

          </div>

          <div className="flex items-center gap-4">

            <Briefcase className="text-cyan-400" />

            <div>

              <p className="text-slate-400">

                Designation

              </p>

              <p className="font-semibold text-white">

                {data.employee.designation}

              </p>

            </div>

          </div>

          <div className="flex items-center gap-4">

            <Mail className="text-cyan-400" />

            <div>

              <p className="text-slate-400">

                Email

              </p>

              <p className="font-semibold text-white">

                {data.employee.email}

              </p>

            </div>

          </div>

        </div>

      </div>

      {/* Behavior Analysis */}

<div className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-8">

  <h2 className="mb-6 text-2xl font-bold text-white">
    Behavior Analysis
  </h2>

  {data.behavior ? (

    <div className="grid grid-cols-1 gap-8 md:grid-cols-2">

      {/* Login Features */}

      <div>

        <h3 className="mb-4 text-xl font-semibold text-cyan-400">
          Login Features
        </h3>

        <FeatureRow label="Login Count" value={data.behavior.login_count} />
        <FeatureRow label="Unique PCs" value={data.behavior.unique_pc_count} />
        <FeatureRow label="Weekend Logins" value={data.behavior.weekend_logins} />
        <FeatureRow label="After-hours Logins" value={data.behavior.after_hours_logins} />
        <FeatureRow label="Average Login Hour" value={data.behavior.average_login_hour} />

      </div>

      {/* HTTP Features */}

      <div>

        <h3 className="mb-4 text-xl font-semibold text-cyan-400">
          HTTP Features
        </h3>

        <FeatureRow label="HTTP Visits" value={data.behavior.http_visit_count} />
        <FeatureRow label="Unique Websites" value={data.behavior.unique_websites} />
        <FeatureRow label="After-hours HTTP" value={data.behavior.after_hours_http} />
        <FeatureRow label="Weekend HTTP" value={data.behavior.weekend_http} />
        <FeatureRow label="Unique HTTP PCs" value={data.behavior.unique_http_pcs} />

      </div>

      {/* Email Features */}

      <div>

        <h3 className="mb-4 text-xl font-semibold text-cyan-400">
          Email Features
        </h3>

        <FeatureRow label="Emails Sent" value={data.behavior.email_sent} />
        <FeatureRow label="External Emails" value={data.behavior.external_emails} />
        <FeatureRow label="After-hours Emails" value={data.behavior.after_hours_emails} />

      </div>

      {/* File Features */}

      <div>

        <h3 className="mb-4 text-xl font-semibold text-cyan-400">
          File Features
        </h3>

        <FeatureRow label="File Access Count" value={data.behavior.file_access_count} />
        <FeatureRow label="Unique Files" value={data.behavior.unique_files} />
        <FeatureRow label="After-hours File Access" value={data.behavior.after_hours_file_access} />
        <FeatureRow label="Weekend File Access" value={data.behavior.weekend_file_access} />

      </div>

      {/* Device Features */}

      <div>

        <h3 className="mb-4 text-xl font-semibold text-cyan-400">
          Device Features
        </h3>

        <FeatureRow label="Device Usage Count" value={data.behavior.device_usage_count} />
        <FeatureRow label="Connect Count" value={data.behavior.connect_count} />
        <FeatureRow label="Disconnect Count" value={data.behavior.disconnect_count} />
        <FeatureRow label="After-hours Device Usage" value={data.behavior.after_hours_device_usage} />
        <FeatureRow label="Weekend Device Usage" value={data.behavior.weekend_device_usage} />

      </div>

    </div>

  ) : (

    <p className="text-slate-400">
      No behavior profile available.
    </p>

  )}

</div>

      {/* Prediction History */}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: .3 }}
        className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-xl"
      >

        <h2 className="mb-6 text-2xl font-bold text-white">

          Prediction History

        </h2>

        <div className="overflow-x-auto">

          <table className="w-full">

            <thead className="border-b border-slate-700 text-slate-400">

              <tr>

                <th className="pb-4 text-left">
                  Login
                </th>

                <th className="pb-4 text-left">
                  Devices
                </th>

                <th className="pb-4 text-left">
                  Hour
                </th>

                <th className="pb-4 text-left">
                  Weekend
                </th>

                <th className="pb-4 text-left">
                  Risk
                </th>

                <th className="pb-4 text-left">
                  Confidence
                </th>

              </tr>

            </thead>

            <tbody>
                            {data.predictions.length === 0 ? (

              <tr>

                <td
                  colSpan="6"
                  className="py-10 text-center text-slate-400"
                >
                  No prediction history available.
                </td>

              </tr>

            ) : (

              data.predictions.map((p) => (

                <tr
                  key={p.id}
                  className="border-b border-slate-800 transition hover:bg-slate-800/40"
                >

                  <td className="py-4">
                    {p.login_count}
                  </td>

                  <td className="py-4">
                    {p.unique_pc_count}
                  </td>

                  <td className="py-4">
                    {p.hour}
                  </td>

                  <td className="py-4">

                    {p.is_weekend ? (

                      <span className="rounded-lg bg-yellow-500/20 px-3 py-1 text-yellow-400">
                        Weekend
                      </span>

                    ) : (

                      <span className="rounded-lg bg-slate-700 px-3 py-1 text-slate-300">
                        Weekday
                      </span>

                    )}

                  </td>

                  <td className="py-4">

                    <span
                      className={`rounded-lg px-3 py-1 font-semibold ${
                        p.risk_level === "HIGH"
                          ? "bg-red-500/20 text-red-400"
                          : "bg-green-500/20 text-green-400"
                      }`}
                    >
                      {p.risk_level}
                    </span>

                  </td>

                  <td className="py-4">

                    <span className="rounded-lg bg-cyan-500/20 px-3 py-1 text-cyan-400">

                      {Number(p.confidence).toFixed(1)}%

                    </span>

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </motion.div>

    </Layout>

  );

}