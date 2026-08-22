import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Tooltip, Legend, Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Tooltip, Legend, Filler,
);

// Read a CSS custom property so the charts use the exact same palette as the
// rest of the console - one source of truth for colour.
export function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Shared defaults so every chart reads as instrumentation, not a slide deck.
ChartJS.defaults.font.family = "'JetBrains Mono', monospace";
ChartJS.defaults.font.size = 11;
ChartJS.defaults.color = '#5f7186';

export const gridColor = 'rgba(42, 54, 70, 0.4)';

export const SEVERITY_COLORS = {
  informational: '#64748b',
  low: '#38bdf8',
  medium: '#fbbf24',
  high: '#fb923c',
  critical: '#f43f5e',
};
