import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { investigate, data } from '../lib/api';
import { Panel, SeverityPill, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './Investigations.css';

// The case file. Enter a user id (or arrive via a queue click), see their
// behavioural baseline, a day-by-day risk timeline, and - the payoff - the SHAP
// explanation of exactly why the model scored any given day.
export default function Investigations() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [input, setInput] = useState(userId || '');

  function submit(e) {
    e.preventDefault();
    const id = input.trim().toUpperCase();
    if (id) navigate(`/investigations/${id}`);
  }

  return (
    <div className="inv">
      <motion.div className="inv__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Case file · why was this flagged</div>
          <h1 className="inv__title">Investigations</h1>
        </div>
        <form className="inv__search" onSubmit={submit}>
          <input value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Employee ID, e.g. INC0003" className="inv__input" />
          <button type="submit" className="btn btn--signal inv__go">Open</button>
        </form>
      </motion.div>

      {!userId ? <CasePrompt />
        : <CaseFile key={userId} userId={userId} />}
    </div>
  );
}

function CasePrompt() {
  const employees = useAsync(() => data.employees({ limit: 500 }), []);
  const navigate = useNavigate();
  // A few starting points - the known insiders make good demos.
  const suggestions = ['INC0001', 'INC0002', 'INC0003', 'MSO0222', 'CSC0217'];
  return (
    <Panel eyebrow="Start here" title="Open a case" delay={0.05}>
      <p className="inv__hint">
        Enter an employee ID above to pull their full behavioural history, or start
        with one of these flagged individuals:
      </p>
      <div className="inv__suggest">
        {suggestions.map((id) => (
          <button key={id} className="inv__chip mono" onClick={() => navigate(`/investigations/${id}`)}>
            {id}
          </button>
        ))}
      </div>
    </Panel>
  );
}

function CaseFile({ userId }) {
  const caseFile = useAsync(() => investigate.caseFile(userId), [userId]);
  const [selectedDay, setSelectedDay] = useState(null);

  if (caseFile.loading) return <Loader label={`Building case on ${userId}`} />;
  if (caseFile.error) return <ErrorNote error={caseFile.error} onRetry={caseFile.reload} />;

  const { employee, baseline, timeline } = caseFile.data;
  // Rank timeline days by risk so the interesting ones surface.
  const alertDays = (timeline || []).filter((d) => d.severity !== 'informational' || d.risk_score > 10);
  const sorted = [...(timeline || [])].sort((a, b) => b.risk_score - a.risk_score);
  const hottest = sorted.slice(0, 30);

  return (
    <div className="casefile">
      {/* subject header */}
      <motion.div className="subject"
        initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
        <div className="subject__id">
          <div className="subject__uid mono">{employee.user_id}</div>
          <div className="subject__name">{employee.name}</div>
        </div>
        <div className="subject__facts">
          <Fact label="Role" value={employee.role} />
          <Fact label="Department" value={employee.department} />
          <Fact label="Team" value={employee.team} />
          <Fact label="Supervisor" value={employee.supervisor} />
        </div>
      </motion.div>

      <div className="casefile__grid">
        {/* baseline */}
        <Panel className="casefile__baseline" eyebrow="Learned behaviour" title="Baseline profile" delay={0.05}>
          <Baseline baseline={baseline} />
        </Panel>

        {/* timeline */}
        <Panel className="casefile__timeline" eyebrow={`${hottest.length} highest-risk days`}
          title="Risk timeline" delay={0.1}>
          {!hottest.length ? <Empty label="No scored days." />
            : (
              <div className="tline">
                {hottest.map((d) => (
                  <button key={d.date}
                    className={`tline__row ${selectedDay?.date === d.date ? 'tline__row--sel' : ''}`}
                    onClick={() => setSelectedDay(d)}>
                    <span className="tline__date mono">{d.date}</span>
                    <SeverityPill severity={d.severity} />
                    <span className="tline__bar">
                      <span className="tline__barfill" style={{ width: `${Math.min(d.risk_score, 100)}%` }} />
                    </span>
                    <span className="tline__score mono">{d.risk_score.toFixed(0)}</span>
                  </button>
                ))}
              </div>
            )}
        </Panel>
      </div>

      {/* explanation - appears when a day is picked */}
      {selectedDay && (
        <Explain userId={userId} day={selectedDay.date} components={selectedDay.components} />
      )}
    </div>
  );
}

function Baseline({ baseline }) {
  const rows = [
    ['Training window', `${baseline.training_days} days`],
    ['Mean logons/day', baseline.mean_logon_count?.toFixed(2)],
    ['Mean USB/day', baseline.mean_usb_connect?.toFixed(3)],
    ['Mean file events/day', baseline.mean_file_events?.toFixed(2)],
    ['Mean after-hours', baseline.mean_after_hours_logon?.toFixed(2)],
  ];
  return (
    <div className="baseline">
      {rows.map(([l, v]) => (
        <div key={l} className="baseline__row">
          <span className="baseline__l">{l}</span>
          <span className="baseline__v mono">{v}</span>
        </div>
      ))}
      <div className="baseline__flags">
        <FlagPill on={baseline.ever_used_usb} label="Ever used USB" />
        <FlagPill on={baseline.ever_worked_after_hours} label="Ever after-hours" />
      </div>
    </div>
  );
}

function Explain({ userId, day, components }) {
  const ex = useAsync(() => investigate.explain(userId, day), [userId, day]);
  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Panel className="explain" eyebrow={`Model reasoning · ${day}`}
        title="Why did the model score this day?">
        {ex.loading ? <Loader label="Computing attribution" />
          : ex.error ? <ErrorNote error={ex.error} onRetry={ex.reload} />
          : (
            <div className="explainbody">
              <div className="explainbody__verdict">
                <div className="verdict__item">
                  <div className="verdict__label eyebrow">Model probability</div>
                  <div className="verdict__val mono">{(ex.data.probability * 100).toFixed(1)}%</div>
                </div>
                <div className="verdict__item">
                  <div className="verdict__label eyebrow">Alert threshold</div>
                  <div className="verdict__val mono">{(ex.data.threshold * 100).toFixed(1)}%</div>
                </div>
                <div className="verdict__item">
                  <div className="verdict__label eyebrow">Verdict</div>
                  <div className={`verdict__badge ${ex.data.would_alert ? 'verdict__badge--alert' : 'verdict__badge--clear'}`}>
                    {ex.data.would_alert ? 'WOULD ALERT' : 'below threshold'}
                  </div>
                </div>
              </div>

              <div className="contrib">
                <div className="contrib__title eyebrow">Top feature contributions</div>
                {(ex.data.contributions || []).map((c) => (
                  <div key={c.feature} className="contrib__row">
                    <span className="contrib__feat mono">{prettyFeature(c.feature)}</span>
                    <span className="contrib__val mono">{c.value?.toFixed(2)}</span>
                    <span className={`contrib__dir contrib__dir--${c.direction}`}>
                      {c.direction === 'increased' ? '▲ raised risk' : '▼ lowered risk'}
                    </span>
                    <span className="contrib__weight mono">+{c.contribution?.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {components && (
                <div className="compbar">
                  <div className="compbar__title eyebrow">Risk components this day</div>
                  {Object.entries(components).map(([k, v]) => (
                    <div key={k} className="compbar__row">
                      <span className="compbar__k">{prettyComponent(k)}</span>
                      <span className="compbar__track">
                        <span className="compbar__fill" style={{ width: `${Math.min(v, 100)}%` }} />
                      </span>
                      <span className="compbar__v mono">{v.toFixed(0)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
      </Panel>
    </motion.div>
  );
}

function Fact({ label, value }) {
  return (
    <div className="fact">
      <div className="fact__l eyebrow">{label}</div>
      <div className="fact__v">{value || '—'}</div>
    </div>
  );
}
function FlagPill({ on, label }) {
  return (
    <span className={`flagpill ${on ? 'flagpill--on' : 'flagpill--off'}`}>
      <span className="flagpill__dot" />{label}
    </span>
  );
}

function prettyFeature(f) {
  return f.replace(/_/g, ' ').replace(/\bz /g, 'z-').replace(/\broll7\b/, '7d');
}
function prettyComponent(c) {
  return c.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase());
}
