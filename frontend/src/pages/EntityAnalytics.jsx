import { useState } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { entity } from '../lib/api';
import { Panel, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './EntityAnalytics.css';

// UEBA - User & Entity Behaviour Analytics. Given an employee, show how they
// behave RELATIVE to their peers and to their own past. This is proactive
// ("profile this entity") where Investigations is reactive ("explain this alert").
export default function EntityAnalytics() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [input, setInput] = useState(userId || '');

  function submit(e) {
    e.preventDefault();
    const id = input.trim().toUpperCase();
    if (id) navigate(`/entity/${id}`);
  }

  return (
    <div className="ent">
      <motion.div className="ent__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">UEBA · entity behaviour analytics</div>
          <h1 className="ent__title">Entity Analytics</h1>
        </div>
        <form className="ent__search" onSubmit={submit}>
          <input value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Employee ID, e.g. INS0001" className="ent__input" />
          <button type="submit" className="btn btn--signal ent__go">Profile</button>
        </form>
      </motion.div>

      {!userId ? <Prompt /> : <Profile key={userId} userId={userId} />}
    </div>
  );
}

function Prompt() {
  const navigate = useNavigate();
  const suggestions = ['INS0001', 'INS0002', 'MSO0222', 'CSC0217'];
  return (
    <Panel eyebrow="Start here" title="Profile an entity" delay={0.05}>
      <p className="ent__hint">
        Enter an employee ID to see how their behaviour compares to their department
        peers and to their own history. Try one of these:
      </p>
      <div className="ent__suggest">
        {suggestions.map((id) => (
          <button key={id} className="ent__chip mono" onClick={() => navigate(`/entity/${id}`)}>{id}</button>
        ))}
      </div>
    </Panel>
  );
}

function Profile({ userId }) {
  const [recentDays, setRecentDays] = useState(30);
  const state = useAsync(() => entity.analytics(userId, recentDays), [userId, recentDays]);

  if (state.loading) return <Loader label={`Profiling ${userId}`} />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;

  const d = state.data;
  if (!d.has_data) {
    return (
      <Panel eyebrow={d.employee.user_id} title={d.employee.name || 'Entity'}>
        <Empty label="No behavioural history for this entity." />
      </Panel>
    );
  }

  return (
    <div className="profile">
      <motion.div className="profile__subject"
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
        <div>
          <div className="profile__uid mono">{d.employee.user_id}</div>
          <div className="profile__name">{d.employee.name}</div>
        </div>
        <div className="profile__facts">
          <Fact l="Department" v={d.employee.department} />
          <Fact l="Role" v={d.employee.role} />
          <Fact l="Team" v={d.employee.team} />
          <Fact l="Observed" v={`${d.window.days_observed} days`} />
        </div>
      </motion.div>

      <div className="profile__grid">
        <Panel className="profile__peer" delay={0.05}
          eyebrow="Standing vs department peers"
          title="How unusual is this person for their team?">
          <PeerStanding rows={d.peer_standing} />
        </Panel>

        <Panel className="profile__drift" delay={0.1}
          eyebrow={`Recent ${d.window.recent_days}d vs earlier history`}
          title="What is drifting?">
          <Drift rows={d.drift} />
        </Panel>
      </div>

      <Panel className="profile__traj" delay={0.15}
        eyebrow={`${d.trajectory.length} alerts`} title="Risk trajectory">
        <Trajectory rows={d.trajectory} />
      </Panel>
    </div>
  );
}

// Peer standing: for each behaviour, TWO signals against the department.
//   - the average bar (sustained deviation): how this person compares day-to-day
//   - the peak marker (worst single day): catches one-off spikes the average hides
// A single-day exfiltration is invisible in the average but lights up the peak,
// so showing both is what stops a one-day attacker from looking innocent.
function PeerStanding({ rows }) {
  if (!rows.length) return <Empty label="No peer group to compare against." />;
  // scale bars against the largest signal present, across both average and peak
  const maxAbs = Math.max(
    ...rows.map((r) => Math.max(Math.abs(r.peer_z), Math.abs(r.peak_z ?? 0))), 1);
  return (
    <div className="peer">
      <div className="peer__heads">
        <span />
        <span className="peer__track-head">
          <span className="peer__hh peer__hh--avg">■ typical day</span>
          <span className="peer__hh peer__hh--peak">◆ worst day</span>
        </span>
        <span />
      </div>
      {rows.map((r) => {
        const avgPct = (Math.abs(r.peer_z) / maxAbs) * 50;
        const above = r.peer_z >= 0;
        const hasPeak = r.peak_z != null && r.peak_z !== r.peer_z;
        // peak marker position: signed, from centre
        const peakPct = hasPeak
          ? Math.max(Math.min((r.peak_z / maxAbs) * 50, 50), -50)
          : null;
        // a peak is "notable" if it clears 2 sigma - worth the eye
        const peakHot = hasPeak && Math.abs(r.peak_z) >= 2;
        return (
          <div key={r.feature} className="peer__row">
            <div className="peer__label">{r.label}</div>
            <div className="peer__track">
              <div className="peer__centre" />
              <div className={`peer__bar ${above ? 'peer__bar--above' : 'peer__bar--below'}`}
                style={above
                  ? { left: '50%', width: `${avgPct}%` }
                  : { right: '50%', width: `${avgPct}%` }} />
              {peakPct != null && (
                <div className={`peer__peak ${peakHot ? 'peer__peak--hot' : ''}`}
                  style={{ left: `calc(50% + ${peakPct}%)` }}
                  title={`worst day: ${r.peak_z > 0 ? '+' : ''}${r.peak_z}σ`} />
              )}
            </div>
            <div className="peer__vals">
              <span className={`peer__z mono ${above ? 'peer__z--above' : 'peer__z--below'}`}>
                {r.peer_z > 0 ? '+' : ''}{r.peer_z}
              </span>
              {hasPeak && (
                <span className={`peer__pk mono ${peakHot ? 'peer__pk--hot' : ''}`}>
                  ◆{r.peak_z > 0 ? '+' : ''}{r.peak_z}
                </span>
              )}
            </div>
          </div>
        );
      })}
      <div className="peer__legend">
        <span>← below peers</span><span>above peers →</span>
      </div>
    </div>
  );
}

function Drift({ rows }) {
  if (!rows.length) return <Empty label="No drift data." />;
  return (
    <div className="drift">
      {rows.map((r) => (
        <div key={r.feature} className="drift__row">
          <div className="drift__label">{r.label}</div>
          <div className="drift__nums mono">
            <span className="drift__prior">{r.prior_mean}</span>
            <span className="drift__arrow">→</span>
            <span className="drift__recent">{r.recent_mean}</span>
          </div>
          <div className="drift__chg">{formatChange(r.pct_change)}</div>
        </div>
      ))}
    </div>
  );
}

function Trajectory({ rows }) {
  if (!rows.length) return <Empty label="No alerts for this entity." />;
  // A simple dot-strip: each alert a dot, coloured by severity, along time.
  return (
    <div className="traj">
      {rows.map((r, i) => (
        <div key={i} className={`traj__dot traj__dot--${r.severity}`}
          title={`${r.date} · ${r.severity} · risk ${r.risk_score}`} />
      ))}
    </div>
  );
}

function formatChange(pct) {
  if (pct === 'new') return <span className="chg chg--new">NEW</span>;
  if (pct == null) return <span className="chg chg--flat">—</span>;
  const up = pct > 0;
  return (
    <span className={`chg ${up ? 'chg--up' : 'chg--down'}`}>
      {up ? '▲' : '▼'} {Math.abs(pct)}%
    </span>
  );
}

function Fact({ l, v }) {
  return (
    <div className="pfact">
      <div className="pfact__l eyebrow">{l}</div>
      <div className="pfact__v">{v || '—'}</div>
    </div>
  );
}
