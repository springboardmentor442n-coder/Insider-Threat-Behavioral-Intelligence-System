import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { notifications as notifApi } from '../lib/api';
import './NotificationBell.css';

// The bell in the header: an unread badge, and a dropdown feed. Polls the unread
// count on an interval so a notification raised elsewhere (an escalation by
// another analyst) shows up without a page reload.
export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);
  const navigate = useNavigate();

  const refreshCount = useCallback(async () => {
    try {
      const { unread } = await notifApi.unreadCount();
      setUnread(unread);
    } catch {
      /* silent - a failed count poll should not surface an error to the user */
    }
  }, []);

  // poll the badge every 20s
  useEffect(() => {
    refreshCount();
    const t = setInterval(refreshCount, 20000);
    return () => clearInterval(t);
  }, [refreshCount]);

  // close on outside click
  useEffect(() => {
    function onClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  async function toggle() {
    const next = !open;
    setOpen(next);
    if (next) {
      setLoading(true);
      try {
        const { notifications } = await notifApi.list(false);
        setItems(notifications);
      } catch {
        setItems([]);
      } finally {
        setLoading(false);
      }
    }
  }

  async function openItem(n) {
    if (!n.is_read) {
      try {
        await notifApi.markRead(n.id);
        setItems((xs) => xs.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
        refreshCount();
      } catch { /* non-fatal */ }
    }
    setOpen(false);
    // deep-link: jump to the subject's entity/investigation view if we have one
    if (n.subject_user_id) navigate(`/investigations/${n.subject_user_id}`);
  }

  async function markAll() {
    try {
      await notifApi.markAllRead();
      setItems((xs) => xs.map((x) => ({ ...x, is_read: true })));
      setUnread(0);
    } catch { /* non-fatal */ }
  }

  return (
    <div className="nbell" ref={ref}>
      <button className="nbell__btn" onClick={toggle} title="Notifications" aria-label="Notifications">
        <span className="nbell__glyph">◔</span>
        {unread > 0 && (
          <motion.span className="nbell__badge"
            initial={{ scale: 0 }} animate={{ scale: 1 }}
            key={unread}>
            {unread > 99 ? '99+' : unread}
          </motion.span>
        )}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div className="nbell__panel"
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.98 }}
            transition={{ duration: 0.14 }}>
            <div className="nbell__head">
              <span className="nbell__title">Notifications</span>
              {items.some((x) => !x.is_read) && (
                <button className="nbell__markall" onClick={markAll}>Mark all read</button>
              )}
            </div>

            <div className="nbell__list">
              {loading ? (
                <div className="nbell__empty">Loading…</div>
              ) : items.length === 0 ? (
                <div className="nbell__empty">No notifications yet.</div>
              ) : (
                items.map((n) => (
                  <button key={n.id}
                    className={`nbell__item ${n.is_read ? '' : 'nbell__item--unread'}`}
                    onClick={() => openItem(n)}>
                    <span className={`nbell__dot nbell__dot--${n.severity || 'informational'}`} />
                    <span className="nbell__body">
                      <span className="nbell__itemtitle">{n.title}</span>
                      <span className="nbell__itemtext">{n.body}</span>
                      <span className="nbell__meta">
                        {n.type.replace('_', ' ')} · {timeAgo(n.created_at)}
                      </span>
                    </span>
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function timeAgo(iso) {
  if (!iso) return '';
  const then = new Date(iso).getTime();
  const secs = Math.max(0, (Date.now() - then) / 1000);
  if (secs < 60) return 'just now';
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`;
  return `${Math.floor(secs / 86400)}d ago`;
}
