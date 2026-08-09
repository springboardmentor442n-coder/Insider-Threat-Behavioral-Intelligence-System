import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus, Search, Eye, ShieldAlert } from 'lucide-react';
import AppLayout from '../../components/layout/AppLayout';
import {
  Spinner, ErrorState, EmptyState, RiskBar,
  Modal, FilterRow, SelectFilter, Pagination
} from '../../components/common';
import { useFetch, usePaginated } from '../../hooks/useFetch';
import { employeeAPI, riskAPI } from '../../api/client';
import { riskBadge, fmtDate, apiError } from '../../utils/helpers';
import toast from 'react-hot-toast';

// ── Create employee modal ─────────────────────────────────────────────────────
function CreateEmployeeModal({ open, onClose, onCreated, departments }) {
  const [form, setForm] = useState({
    employee_id: '', full_name: '', email: '', designation: '',
    department_id: '', access_level: 'standard',
  });
  const [saving, setSaving] = useState(false);

  const handle = async e => {
    e.preventDefault(); setSaving(true);
    try {
      await employeeAPI.create({
        ...form,
        department_id: form.department_id ? Number(form.department_id) : null,
      });
      toast.success('Employee created');
      onCreated(); onClose();
      setForm({ employee_id:'', full_name:'', email:'', designation:'', department_id:'', access_level:'standard' });
    } catch (err) {
      toast.error(apiError(err));
    } finally { setSaving(false); }
  };

  return (
    <Modal open={open} onClose={onClose} title="Onboard New Employee">
      <form onSubmit={handle}>
        {[
          ['employee_id','Employee ID','EMP001'],
          ['full_name',  'Full Name',  'Alice Johnson'],
          ['email',      'Email',      'alice@company.com'],
          ['designation','Designation','Senior Engineer'],
        ].map(([key, label, ph]) => (
          <div className="form-group" key={key}>
            <label className="form-label">{label}</label>
            <input className="form-input" placeholder={ph} required={key !== 'designation'}
              value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} />
          </div>
        ))}

        <div className="form-group">
          <label className="form-label">Department</label>
          <select className="form-input" value={form.department_id}
            onChange={e => setForm(f => ({ ...f, department_id: e.target.value }))}>
            <option value="">— Select —</option>
            {(departments || []).map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Access Level</label>
          <select className="form-input" value={form.access_level}
            onChange={e => setForm(f => ({ ...f, access_level: e.target.value }))}>
            <option value="standard">Standard</option>
            <option value="elevated">Elevated</option>
            <option value="privileged">Privileged</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 8 }}>
          <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Creating…' : 'Create Employee'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

// ── Employees list page ───────────────────────────────────────────────────────
export default function EmployeesPage() {
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);
  const [search,     setSearch]     = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [scoring,    setScoring]    = useState(false);

  const { data: depts } = useFetch(() => employeeAPI.departments().then(r => r.data));

  const { data, loading, error, refetch, page, setPage, updateParams } = usePaginated(
    params => employeeAPI.list(params).then(r => r.data), {}, 20
  );

  const handleSearch = () => updateParams({ search, department_id: deptFilter || undefined });

  const scoreAll = async () => {
    setScoring(true);
    try {
      await riskAPI.scoreAll();
      toast.success('Risk scoring queued for all employees');
    } catch (err) {
      toast.error(apiError(err));
    } finally { setScoring(false); }
  };

  return (
    <AppLayout title="Employee Management" subtitle="Monitor and manage all employees">
      <div className="page-header">
        <div />
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-ghost" onClick={scoreAll} disabled={scoring}>
            <ShieldAlert size={14} /> {scoring ? 'Scoring…' : 'Score All'}
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <UserPlus size={14} /> Add Employee
          </button>
        </div>
      </div>

      {/* Filters */}
      <FilterRow>
        <div style={{ position: 'relative', flex: 1, maxWidth: 300 }}>
          <Search size={13} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" placeholder="Search name, ID, email…"
            style={{ paddingLeft: 32 }} value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()} />
        </div>
        <SelectFilter value={deptFilter} onChange={v => { setDeptFilter(v); updateParams({ department_id: v || undefined, search }); }}
          options={(depts || []).map(d => ({ value: String(d.id), label: d.name }))}
          placeholder="All Departments" />
        <button className="btn btn-ghost" onClick={handleSearch}>Search</button>
      </FilterRow>

      {/* Table */}
      <div className="card" style={{ padding: 0 }}>
        {loading ? <Spinner /> : error ? <ErrorState message={error} /> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Department</th>
                  <th>Access Level</th>
                  <th>Hire Date</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {(Array.isArray(data) ? data : []).map(emp => (
                  <tr key={emp.id}>
                    <td><span className="mono">{emp.employee_id}</span></td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{emp.full_name}</td>
                    <td>{emp.email}</td>
                    <td>{emp.department_id || '—'}</td>
                    <td>
                      <span style={{
                        fontSize: '0.72rem', padding: '2px 8px', borderRadius: 20,
                        background: emp.access_level === 'privileged' ? 'var(--risk-critical-bg)' :
                                    emp.access_level === 'elevated'   ? 'var(--risk-medium-bg)' : 'var(--bg-hover)',
                        color: emp.access_level === 'privileged' ? 'var(--risk-critical)' :
                               emp.access_level === 'elevated'   ? 'var(--risk-medium)' : 'var(--text-muted)',
                      }}>{emp.access_level}</span>
                    </td>
                    <td>{fmtDate(emp.hire_date)}</td>
                    <td>
                      <span style={{
                        fontSize: '0.72rem', padding: '2px 8px', borderRadius: 20,
                        background: emp.is_active ? 'var(--risk-low-bg)' : 'var(--bg-hover)',
                        color: emp.is_active ? 'var(--risk-low)' : 'var(--text-muted)',
                      }}>
                        {emp.is_terminated ? 'Terminated' : emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-ghost" style={{ padding: '5px 10px', fontSize: '0.78rem' }}
                        onClick={() => navigate(`/employees/${emp.id}`)}>
                        <Eye size={12} /> View
                      </button>
                    </td>
                  </tr>
                ))}
                {!data?.length && <tr><td colSpan={8}><EmptyState message="No employees found" /></td></tr>}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <Pagination page={page} setPage={setPage} hasMore={data?.length === 20} pageSize={20} />}
      </div>

      <CreateEmployeeModal open={showCreate} onClose={() => setShowCreate(false)}
        onCreated={refetch} departments={depts} />
    </AppLayout>
  );
}
