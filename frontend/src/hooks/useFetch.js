import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Generic fetch hook with loading / error / refetch.
 * fn: async () => response.data
 */
export function useFetch(fn, deps = []) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const mounted = useRef(true);

  const run = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const result = await fn();
      if (mounted.current) setData(result);
    } catch (e) {
      if (mounted.current) setError(e?.response?.data?.detail || e.message);
    } finally {
      if (mounted.current) setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    mounted.current = true;
    run();
    return () => { mounted.current = false; };
  }, [run]);

  return { data, loading, error, refetch: run };
}

/** Auto-refreshing fetch. intervalMs default = 30s */
export function usePolling(fn, deps = [], intervalMs = 30000) {
  const { data, loading, error, refetch } = useFetch(fn, deps);

  useEffect(() => {
    const id = setInterval(refetch, intervalMs);
    return () => clearInterval(id);
  }, [refetch, intervalMs]);

  return { data, loading, error, refetch };
}

/** Paginated list hook */
export function usePaginated(fetchFn, extraParams = {}, pageSize = 20) {
  const [page,    setPage]    = useState(1);
  const [params,  setParams]  = useState(extraParams);

  const { data, loading, error, refetch } = useFetch(
    () => fetchFn({ page, page_size: pageSize, ...params }),
    [page, JSON.stringify(params)]
  );

  const updateParams = useCallback((next) => {
    setParams(p => ({ ...p, ...next }));
    setPage(1);
  }, []);

  return { data: data || [], loading, error, refetch, page, setPage, updateParams };
}
