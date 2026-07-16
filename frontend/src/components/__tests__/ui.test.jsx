import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ErrorNote, SeverityPill } from '../ui';

// This is a regression test for a real bug: a FastAPI 422 returns `detail` as an
// ARRAY of objects, and rendering that array directly crashed React with
// "Objects are not valid as a React child". ErrorNote must coerce any detail
// shape - string, array, or object - to readable text.
describe('ErrorNote', () => {
  it('renders a string detail as-is', () => {
    render(<ErrorNote error={{ status: 400, detail: 'Something broke' }} />);
    expect(screen.getByText('Something broke')).toBeInTheDocument();
  });

  it('coerces a FastAPI 422 array detail to text instead of crashing', () => {
    const error = {
      status: 422,
      detail: [
        { type: 'json_invalid', loc: ['body', 1], msg: 'JSON decode error', input: {} },
      ],
    };
    // The key assertion: this renders without throwing, and shows the msg.
    render(<ErrorNote error={error} />);
    expect(screen.getByText(/JSON decode error/)).toBeInTheDocument();
  });

  it('shows a friendly message for a 403', () => {
    render(<ErrorNote error={{ status: 403 }} />);
    expect(screen.getByText(/do not have access/i)).toBeInTheDocument();
  });
});

describe('SeverityPill', () => {
  it('renders the severity label and count', () => {
    render(<SeverityPill severity="critical" count={12} />);
    expect(screen.getByText('critical')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });
});
