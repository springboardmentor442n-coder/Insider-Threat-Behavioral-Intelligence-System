import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

// Mock the API module. Crucially, the mocked top-risks response INCLUDES an
// `is_insider` field (and an employee_name). The backend's real endpoint strips
// is_insider, but if it ever regressed and leaked it, the FRONTEND must still
// not render it. This test pins that guarantee independently of the backend.
vi.mock('../../../lib/api', () => ({
  dashboard: {
    riskTrend: vi.fn().mockResolvedValue({ days: 30, total_alerts: 3, series: [
      { date: '2011-05-01', critical: 1, high: 1, medium: 0, low: 0, informational: 0 },
    ]}),
    anomalyBreakdown: vi.fn().mockResolvedValue({ alerts_considered: 3, components: [
      { component: 'behavioral_anomalies', average: 75 },
    ]}),
    topRisks: vi.fn().mockResolvedValue({ employees: [
      // NOTE the is_insider: true here - ground truth that must NOT reach the DOM
      { user_id: 'MSO0222', department: '6 - Security', peak_risk_score: 80,
        alert_count: 22, is_insider: true, employee_name: 'Secret Realname' },
      { user_id: 'CSC0217', department: '6 - Security', peak_risk_score: 79,
        alert_count: 23, is_insider: false },
    ]}),
  },
  alerts: {
    summary: vi.fn().mockResolvedValue({
      total: 100, open: 90, unassigned_open: 88,
      by_severity: { critical: 5, high: 10, medium: 20, low: 5, informational: 60 },
    }),
  },
}));

import AnalystDashboard from '../AnalystDashboard';

describe('AnalystDashboard security', () => {
  it('renders the watch-list from top-risks', async () => {
    render(<AnalystDashboard />);
    await waitFor(() => expect(screen.getByText('MSO0222')).toBeInTheDocument());
    expect(screen.getByText('CSC0217')).toBeInTheDocument();
  });

  it('NEVER renders is_insider ground truth, even if the API leaks it', async () => {
    const { container } = render(<AnalystDashboard />);
    await waitFor(() => expect(screen.getByText('MSO0222')).toBeInTheDocument());
    // The words "insider" / "is_insider" must appear nowhere in the rendered DOM.
    const html = container.innerHTML.toLowerCase();
    expect(html).not.toContain('is_insider');
    expect(html).not.toContain('insider');
    // And the flag value / secret name we planted must not be shown.
    expect(screen.queryByText(/secret realname/i)).toBeNull();
  });

  it('shows the real risk scores and counts', async () => {
    render(<AnalystDashboard />);
    await waitFor(() => expect(screen.getByText('MSO0222')).toBeInTheDocument());
    expect(screen.getByText('80')).toBeInTheDocument();  // peak risk
    expect(screen.getByText('79')).toBeInTheDocument();
  });
});
