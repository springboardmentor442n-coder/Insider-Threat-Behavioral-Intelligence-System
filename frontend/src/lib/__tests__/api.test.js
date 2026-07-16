import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getAccessToken, setTokens, clearTokens } from '../api';

// The token store is the security-critical part of the client: it must persist
// across reloads (localStorage) and clear cleanly on logout. These tests pin
// that behaviour so a refactor can't silently break session handling.
describe('token storage', () => {
  beforeEach(() => { localStorage.clear(); });

  it('stores and retrieves an access token', () => {
    setTokens('access-abc', 'refresh-xyz');
    expect(getAccessToken()).toBe('access-abc');
  });

  it('clears both tokens on logout', () => {
    setTokens('access-abc', 'refresh-xyz');
    clearTokens();
    expect(getAccessToken()).toBeNull();
  });

  it('does not overwrite an existing token when passed undefined', () => {
    setTokens('access-abc', 'refresh-xyz');
    setTokens(undefined, undefined);
    expect(getAccessToken()).toBe('access-abc');
  });
});
