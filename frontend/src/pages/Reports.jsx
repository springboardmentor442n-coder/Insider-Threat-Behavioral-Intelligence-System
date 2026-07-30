import { useState } from 'react';
import { motion } from 'framer-motion';
import { reports } from '../lib/api';
import { Panel, useAsync, ErrorNote, Empty } from '../components/ui';
import Loader from '../components/Loader';
import './Reports.css';

// A short human blurb per report, so the page explains what each one is for
// rather than just listing slugs.
const BLURB = {
  'insider-threat':
    'The highest-risk employees ranked by their peak alert score, with the alert evidence behind each.',
  'behavioral-analytics':
    'Organisation-wide behavioural statistics: population averages, baseline coverage, and alert load by department.',
  investigation:
    'One employee\u2019s full case file \u2014 identity, behavioural baseline, and alert timeline. Requires a user ID.',
  compliance:
    'The audit trail and alert-handling metrics: resolution rates, operator actions, and attribution. Administrators only.',
  'risk-assessment':
    'Organisation-wide security posture: severity distribution and the monthly alert trend.',
};

export default function Reports() {
  const catalog = useAsync(() => reports.catalog(), []);
  const list = catalog.data?.reports || [];

  // per-report input for the investigation user_id, and per-button busy state
  const [userIds, setUserIds] = useState({});
  const [busy, setBusy] = useState(null); // `${slug}:${fmt}` while downloading
  const [error, setError] = useState(null);
  const [done, setDone] = useState(null); // last filename downloaded

  async function grab(slug, fmt, needsUser) {
    setError(null);
    setDone(null);
    const uid = (userIds[slug] || '').trim();
    if (needsUser && !uid) {
      setError('This report needs a user ID (e.g. AAM0658).');
      return;
    }
    setBusy(`${slug}:${fmt}`);
    try {
      const filename = await reports.download(slug, fmt, needsUser ? uid : undefined);
      setDone(filename);
    } catch (e) {
      setError(e.message || 'Report failed.');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="rep">
      <motion.div className="rep__head"
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div>
          <div className="eyebrow">Reports &amp; Export</div>
          <h1 className="rep__title">Reports</h1>
        </div>
        <p className="rep__lede">
          Generate a formatted report as PDF (for reading and filing) or Excel
          (for filtering and analysis). Reports are built from live data at the
          moment you download them.
        </p>
      </motion.div>

      {error && <ErrorNote error={error} />}
      {done && (
        <motion.div className="rep__toast"
          initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }}>
          Downloaded <strong>{done}</strong>
        </motion.div>
      )}

      {catalog.loading ? (
        <Loader label="Loading report catalog\u2026" />
      ) : catalog.error ? (
        <ErrorNote error={catalog.error} />
      ) : list.length === 0 ? (
        <Empty>No reports available.</Empty>
      ) : (
        <div className="rep__grid">
          {list.map((r) => (
            <Panel key={r.slug} className="rep__card">
              <div className="rep__card-head">
                <h2 className="rep__card-title">{r.label}</h2>
                {r.slug === 'compliance' && (
                  <span className="rep__badge">Admin</span>
                )}
              </div>
              <p className="rep__card-blurb">{BLURB[r.slug] || ''}</p>

              {r.needs_user_id && (
                <input
                  className="rep__uid"
                  placeholder="User ID (e.g. AAM0658)"
                  value={userIds[r.slug] || ''}
                  onChange={(e) =>
                    setUserIds((m) => ({ ...m, [r.slug]: e.target.value }))
                  }
                />
              )}

              <div className="rep__actions">
                {r.formats.map((fmt) => (
                  <button
                    key={fmt}
                    className={`rep__btn rep__btn--${fmt}`}
                    disabled={busy === `${r.slug}:${fmt}`}
                    onClick={() => grab(r.slug, fmt, r.needs_user_id)}
                  >
                    {busy === `${r.slug}:${fmt}`
                      ? 'Generating\u2026'
                      : `Download ${fmt.toUpperCase()}`}
                  </button>
                ))}
              </div>
            </Panel>
          ))}
        </div>
      )}
    </div>
  );
}
