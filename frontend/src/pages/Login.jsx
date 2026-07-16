import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { gsap } from 'gsap';
import { useAuth } from '../context/AuthContext';
import { ApiError } from '../lib/api';
import './Login.css';

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const scanRef = useRef(null);

  // A slow vertical sweep across the panel - like a document under a scanner.
  // Ambient, not attention-grabbing; it just says "this is a forensic tool".
  useEffect(() => {
    if (!scanRef.current) return;
    const tl = gsap.timeline({ repeat: -1, repeatDelay: 2.5 });
    tl.fromTo(
      scanRef.current,
      { yPercent: -100, opacity: 0 },
      { yPercent: 700, opacity: 0.7, duration: 2.4, ease: 'power1.inOut' },
    ).to(scanRef.current, { opacity: 0, duration: 0.3 }, '-=0.3');
    return () => tl.kill();
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await login(email, password);
      // App.jsx redirects on user state change.
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError('Those credentials were not recognised.');
      } else if (err instanceof ApiError && err.status === 429) {
        setError('Too many attempts. Wait a moment before trying again.');
      } else {
        setError('Could not reach the server. Is the backend running?');
      }
      setBusy(false);
    }
  }

  return (
    <div className="login">
      <div className="login__aside">
        <motion.div
          className="login__brand"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="login__mark">
            <span className="login__mark-glyph" />
            ITBIS
          </div>
          <h1 className="login__headline">
            Insider Threat<br />Behavioral Intelligence
          </h1>
          <p className="login__sub">
            Per-user behavioural baselines. Deviation scoring. Evidence you can
            take to a tribunal.
          </p>
          <div className="login__stats">
            <Stat n="1,000" l="employees under watch" />
            <Stat n="32.7M" l="events analysed" />
            <Stat n="0.00061" l="false-positive rate" mono />
          </div>
        </motion.div>
      </div>

      <div className="login__main">
        <motion.form
          className="login__form"
          onSubmit={onSubmit}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          <div ref={scanRef} className="login__scanline" />

          <div className="eyebrow login__eyebrow">Operator access</div>
          <h2 className="login__title">Sign in to the console</h2>

          <label className="field">
            <span className="field__label">Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@dtaa.com"
              autoComplete="username"
              required
              autoFocus
            />
          </label>

          <label className="field">
            <span className="field__label">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              autoComplete="current-password"
              required
            />
          </label>

          {error && (
            <motion.div
              className="login__error"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
            >
              {error}
            </motion.div>
          )}

          <button type="submit" className="btn btn--signal login__submit" disabled={busy}>
            {busy ? 'Verifying…' : 'Sign in'}
          </button>

          <p className="login__hint">
            Accounts are provisioned by an administrator. No self-service sign-up.
          </p>
        </motion.form>
      </div>
    </div>
  );
}

function Stat({ n, l, mono }) {
  return (
    <div className="login__stat">
      <div className={`login__stat-n ${mono ? 'mono' : ''}`}>{n}</div>
      <div className="login__stat-l">{l}</div>
    </div>
  );
}
