// src/features/employees/components/RiskBadge.jsx
import { ShieldAlert, ShieldCheck, Shield, ShieldX } from 'lucide-react';

const RISK_CONFIG = {
  low: {
    label: 'Low',
    icon: ShieldCheck,
    classes: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  },
  medium: {
    label: 'Medium',
    icon: Shield,
    classes: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  },
  high: {
    label: 'High',
    icon: ShieldAlert,
    classes: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  },
  critical: {
    label: 'Critical',
    icon: ShieldX,
    classes: 'bg-red-500/10 text-red-400 border-red-500/30 animate-pulse',
  },
};

/**
 * @param {{ level: 'low'|'medium'|'high'|'critical', score?: number }} props
 */
export default function RiskBadge({ level, score }) {
  const config = RISK_CONFIG[level?.toLowerCase()] ?? RISK_CONFIG.low;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${config.classes}`}
    >
      <Icon size={12} strokeWidth={2.5} />
      {config.label}
      {typeof score === 'number' && (
        <span className="opacity-70 tabular-nums">{score.toFixed(0)}</span>
      )}
    </span>
  );
}
