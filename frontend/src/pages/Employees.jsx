import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { data } from '../lib/api';
import { Panel, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './Employees.css';

// The monitored-population directory. Search + filter across all employees, then
// click through to a case file. No risk labels here - this is the roster, not
// the watch-list (that separation matters: it does not leak ground truth).
export default function Employees() {
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [dept, setDept] = useState('');
  // The backend caps limit at 500, so pull every employee in pages of 500 and
  // stitch them together. ~1,000 employees = two requests.
  const all = useAsync(async () => {
    const PAGE = 500;
    let offset = 0;
    let out = [];
    // Guard against runaway loops; the population is ~1,000.
    for (let i = 0; i < 20; i++) {
      const batch = await data.employees({ limit: PAGE, offset });
      if (!Array.isArray(batch) || batch.length === 0) break;
      out = out.concat(batch);
      if (batch.length < PAGE) break;
      offset += PAGE;
    }
    return out;
  }, []);

  const employees = Array.isArray(all.data) ? all.data : [];

  const departments = useMemo(() => {
    const set = new Set(employees.map((e) => e.department).filter(Boolean));
    return [...set].sort();
  }, [employees]);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return employees.filter((e) => {
      if (dept && e.department !== dept) return false;
      if (!needle) return true;
      return (e.user_id || '').toLowerCase().includes(needle)
        || (e.employee_name || '').toLowerCase().includes(needle)
        || (e.role || '').toLowerCase().includes(needle);
    });
  }, [employees, q, dept]);

  return (
    <div className="emp">
      <motion.div className="emp__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Monitored population</div>
          <h1 className="emp__title">Employees</h1>
        </div>
      </motion.div>

      <Panel delay={0.05}
        eyebrow={all.loading ? 'Loading' : `${filtered.length} of ${employees.length} shown`}
        title="Directory"
        action={
          <div className="emp__controls">
            <input value={q} onChange={(e) => setQ(e.target.value)}
              placeholder="Search id, name, role" className="emp__search" />
            <select value={dept} onChange={(e) => setDept(e.target.value)} className="emp__dept">
              <option value="">All departments</option>
              {departments.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        }>
        {all.loading ? <Loader label="Loading roster" />
          : all.error ? <ErrorNote error={all.error} onRetry={all.reload} />
          : !filtered.length ? <Empty label="No employees match." />
          : (
            <div className="emptable">
              <div className="emptable__head">
                <div>Employee</div>
                <div>Role</div>
                <div>Department</div>
                <div>Team</div>
                <div>Supervisor</div>
              </div>
              <div className="emptable__body">
                {filtered.slice(0, 300).map((e, i) => (
                  <motion.button key={e.user_id} className="emprow"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    transition={{ delay: Math.min(i * 0.006, 0.3) }}
                    onClick={() => navigate(`/investigations/${e.user_id}`)}
                    title="Open case file">
                    <div className="emprow__id">
                      <span className="emprow__uid mono">{e.user_id}</span>
                      <span className="emprow__name">{e.employee_name}</span>
                    </div>
                    <div className="emprow__role">{e.role || '—'}</div>
                    <div className="emprow__dept">{e.department || '—'}</div>
                    <div className="emprow__team">{e.team || '—'}</div>
                    <div className="emprow__sup">{e.supervisor || '—'}</div>
                  </motion.button>
                ))}
                {filtered.length > 300 && (
                  <div className="emptable__more mono">
                    Showing first 300 of {filtered.length} — narrow your search to see more.
                  </div>
                )}
              </div>
            </div>
          )}
      </Panel>
    </div>
  );
}
