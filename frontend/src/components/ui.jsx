import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import './ui.css';

// A tiny data-fetching hook. Returns {data, error, loading, reload}. Keeps every
// dashboard card from re-implementing the same try/catch/loading dance.
export function useAsync(fn, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const run = useCallback(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(run, [run]);
  return { ...state, reload: run };
}

export function Panel({ title, eyebrow, action, children, className = '', delay = 0 }) {
  return (
    <motion.section
      className={`panel ${className}`}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {(title || eyebrow || action) && (
        <header className="panel__head">
          <div>
            {eyebrow && <div className="eyebrow">{eyebrow}</div>}
            {title && <h3 className="panel__title">{title}</h3>}
          </div>
          {action}
        </header>
      )}
      <div className="panel__body">{children}</div>
    </motion.section>
  );
}

export function Metric({ label, value, sub, tone = 'default', mono = true }) {
  return (
    <div className={`metric metric--${tone}`}>
      <div className="metric__label eyebrow">{label}</div>
      <div className={`metric__value ${mono ? 'mono' : ''}`}>{value}</div>
      {sub && <div className="metric__sub">{sub}</div>}
    </div>
  );
}

const SEV_ORDER = ['critical', 'high', 'medium', 'low', 'informational'];
export function SeverityPill({ severity, count }) {
  return (
    <span className={`sevpill sevpill--${severity}`}>
      <span className="sevpill__dot" />
      <span className="sevpill__label">{severity}</span>
      {count != null && <span className="sevpill__count mono">{count}</span>}
    </span>
  );
}
export { SEV_ORDER };

// FastAPI returns validation errors (422) as an array of {msg, loc, ...} objects,
// permission errors as a string, and sometimes a bare object. Coerce any of these
// to a readable string so we never hand React a raw object to render.
function detailToText(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg || (typeof d === 'string' ? d : JSON.stringify(d))).join('; ');
  }
  if (typeof detail === 'object') return detail.msg || JSON.stringify(detail);
  return String(detail);
}

export function ErrorNote({ error, onRetry }) {
  const msg = error?.status === 403
    ? 'You do not have access to this view.'
    : detailToText(error?.detail) || 'Could not load this data.';
  return (
    <div className="errnote">
      <div className="errnote__msg">{msg}</div>
      {onRetry && error?.status !== 403 && (
        <button className="errnote__retry" onClick={onRetry}>Retry</button>
      )}
    </div>
  );
}

export function Empty({ label }) {
  return <div className="empty">{label}</div>;
}
