import { X, ChevronLeft, ChevronRight } from 'lucide-react';
import { scoreColor } from '../../utils/helpers';

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 24 }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 32 }}>
      <svg width={size} height={size} viewBox="0 0 24 24"
        style={{ animation: 'spin 0.8s linear infinite' }}>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <circle cx="12" cy="12" r="10" fill="none"
          stroke="var(--border-light)" strokeWidth="3" />
        <path d="M12 2a10 10 0 0 1 10 10" fill="none"
          stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />
      </svg>
    </div>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────────────
export function StatCard({ label, value, delta, icon: Icon, color, onClick }) {
  return (
    <div className="stat-card" onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default',
               borderLeft: color ? `3px solid ${color}` : undefined }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <span className="stat-label">{label}</span>
        {Icon && (
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: color ? `${color}18` : 'var(--bg-hover)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Icon size={15} color={color || 'var(--text-muted)'} />
          </div>
        )}
      </div>
      <div className="stat-value">{value ?? '—'}</div>
      {delta && <div className="stat-delta">{delta}</div>}
    </div>
  );
}

// ── Risk score bar ────────────────────────────────────────────────────────────
export function RiskBar({ score, showLabel = true }) {
  const color = scoreColor(score);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div className="risk-bar-wrap" style={{ flex: 1 }}>
        <div className="risk-bar"
          style={{ width: `${Math.min(score, 100)}%`, background: color }} />
      </div>
      {showLabel && (
        <span className="mono" style={{ fontSize: '0.8rem', color, minWidth: 30 }}>
          {score?.toFixed(0)}
        </span>
      )}
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────
export function EmptyState({ icon: Icon, message = 'No data found' }) {
  return (
    <div className="empty-state">
      {Icon && <Icon size={40} strokeWidth={1} />}
      <p>{message}</p>
    </div>
  );
}

// ── Error state ───────────────────────────────────────────────────────────────
export function ErrorState({ message }) {
  return (
    <div style={{ textAlign: 'center', padding: 40, color: 'var(--risk-critical)' }}>
      <p style={{ fontSize: '0.88rem' }}>⚠ {message || 'Failed to load data'}</p>
    </div>
  );
}

// ── Pagination ────────────────────────────────────────────────────────────────
export function Pagination({ page, setPage, hasMore, total, pageSize }) {
  const totalPages = total ? Math.ceil(total / pageSize) : null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
      gap: 8, marginTop: 16, paddingTop: 16,
      borderTop: '1px solid var(--border)',
    }}>
      {total != null && (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginRight: 'auto' }}>
          {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, total)} of {total}
        </span>
      )}
      <button className="btn btn-ghost" onClick={() => setPage(p => p - 1)}
        disabled={page === 1} style={{ padding: '6px 10px' }}>
        <ChevronLeft size={14} />
      </button>
      <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', minWidth: 60, textAlign: 'center' }}>
        {totalPages ? `${page} / ${totalPages}` : `Page ${page}`}
      </span>
      <button className="btn btn-ghost" onClick={() => setPage(p => p + 1)}
        disabled={!hasMore && (!totalPages || page >= totalPages)}
        style={{ padding: '6px 10px' }}>
        <ChevronRight size={14} />
      </button>
    </div>
  );
}

// ── Modal ─────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children, width = 480 }) {
  if (!open) return null;
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 999,
      background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24,
    }} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)', width: '100%', maxWidth: width,
        maxHeight: '90vh', display: 'flex', flexDirection: 'column',
        boxShadow: 'var(--shadow)',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 20px', borderBottom: '1px solid var(--border)',
        }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 700 }}>{title}</h2>
          <button onClick={onClose} style={{ color: 'var(--text-muted)', padding: 4 }}>
            <X size={16} />
          </button>
        </div>
        <div style={{ padding: 20, overflowY: 'auto', flex: 1 }}>{children}</div>
      </div>
    </div>
  );
}

// ── Section header ────────────────────────────────────────────────────────────
export function SectionHeader({ title, subtitle, action }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
      marginBottom: 16,
    }}>
      <div>
        <h2 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>{title}</h2>
        {subtitle && <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

// ── Filter row ────────────────────────────────────────────────────────────────
export function FilterRow({ children }) {
  return (
    <div style={{
      display: 'flex', gap: 10, marginBottom: 18, flexWrap: 'wrap',
      alignItems: 'center',
    }}>
      {children}
    </div>
  );
}

// ── Select filter ─────────────────────────────────────────────────────────────
export function SelectFilter({ value, onChange, options, placeholder }) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)}
      className="form-input" style={{ width: 'auto', minWidth: 130, padding: '7px 10px' }}>
      <option value="">{placeholder || 'All'}</option>
      {options.map(o => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}
