import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { motion } from "framer-motion";
import { Search, Eye, Users } from "lucide-react";

import Layout from "../components/Layout";

export default function Employee() {
  const navigate = useNavigate();

  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    const filtered = employees.filter((emp) => {
      const query = search.toLowerCase();

      return (
        emp.employee_id?.toLowerCase().includes(query) ||
        emp.name?.toLowerCase().includes(query) ||
        emp.department?.toLowerCase().includes(query) ||
        emp.designation?.toLowerCase().includes(query)
      );
    });

    setFilteredEmployees(filtered);
  }, [search, employees]);

  async function fetchEmployees() {
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/employees"
      );

      setEmployees(res.data);
      setFilteredEmployees(res.data);

    } catch (err) {
      console.error(err);
    }
  }

  return (
    <Layout title="Employee Monitoring">

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >

        <h2 className="text-4xl font-bold text-white">
          Employees
        </h2>

        <p className="mt-2 text-slate-400">
          View and monitor employee information.
        </p>

      </motion.div>

      <div className="mt-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div className="relative w-full md:w-96">

          <Search
            size={18}
            className="absolute left-4 top-3.5 text-slate-400"
          />

          <input
            type="text"
            placeholder="Search employee..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-900 py-3 pl-11 pr-4 text-white outline-none focus:border-cyan-400"
          />

        </div>

        <div className="flex items-center gap-3 rounded-xl border border-slate-700 bg-slate-900 px-5 py-3">

          <Users className="text-cyan-400" />

          <span className="font-semibold text-white">
            {filteredEmployees.length} Employees
          </span>

        </div>

      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: .3 }}
        className="mt-8 overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-xl"
      >

        <table className="w-full">

          <thead className="bg-slate-800 text-slate-300">

            <tr>

              <th className="px-6 py-4 text-left">
                Employee ID
              </th>

              <th className="px-6 py-4 text-left">
                Name
              </th>

              <th className="px-6 py-4 text-left">
                Department
              </th>

              <th className="px-6 py-4 text-left">
                Designation
              </th>

              <th className="px-6 py-4 text-left">
                Email
              </th>

              <th className="px-6 py-4 text-center">
                Action
              </th>

            </tr>

          </thead>

          <tbody>
                        {filteredEmployees.length === 0 ? (

              <tr>

                <td
                  colSpan="6"
                  className="py-12 text-center text-slate-400"
                >
                  No employees found.
                </td>

              </tr>

            ) : (

              filteredEmployees.map((emp, index) => (

                <tr
                  key={emp.employee_id || index}
                  className="border-t border-slate-800 transition-all hover:bg-slate-800/40"
                >

                  <td className="px-6 py-4 font-medium text-cyan-400">
                    {emp.employee_id}
                  </td>

                  <td className="px-6 py-4 text-white">
                    {emp.name}
                  </td>

                  <td className="px-6 py-4 text-slate-300">
                    {emp.department}
                  </td>

                  <td className="px-6 py-4 text-slate-300">
                    {emp.designation}
                  </td>

                  <td className="px-6 py-4 text-slate-400">
                    {emp.email}
                  </td>

                  <td className="px-6 py-4 text-center">

                    <button
                      onClick={() =>
                        navigate(`/employee/${emp.employee_id}`)
                      }
                      className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 font-medium text-white transition hover:bg-cyan-600"
                    >
                      <Eye size={16} />
                      View
                    </button>

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