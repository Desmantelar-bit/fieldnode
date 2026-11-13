'use client';

import { useEffect, useState } from 'react';

export type PollingState<T> = { data: T | undefined; error: unknown; loading: boolean; refresh: () => void };

export function usePolling<T>(fetcher: (signal: AbortSignal) => Promise<T>, ms: number, enabled = true): PollingState<T> {
  const [result, setResult] = useState<{ fetcher: typeof fetcher; data: T }>();
  const [failure, setFailure] = useState<{ fetcher: typeof fetcher; error: unknown }>();
  const [loading, setLoading] = useState(enabled);
  const [revision, setRevision] = useState(0);
  const data = result?.fetcher === fetcher ? result.data : undefined;
  const error = failure?.fetcher === fetcher ? failure.error : undefined;

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    let mounted = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let controller: AbortController | undefined;
    let running = false;

    const run = async () => {
      if (!mounted || document.visibilityState === 'hidden' || running) return;
      running = true;
      controller = new AbortController();
      try {
        const result = await fetcher(controller.signal);
        if (mounted && !controller.signal.aborted) {
          setResult({ fetcher, data: result });
          setFailure(undefined);
        }
      } catch (caught) {
        if (mounted && !controller.signal.aborted) setFailure({ fetcher, error: caught });
      } finally {
        running = false;
        controller = undefined;
        if (mounted) setLoading(false);
        if (mounted && isVisible()) timer = setTimeout(run, Math.max(ms, 1000));
      }
    };

    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        if (timer) clearTimeout(timer);
        controller?.abort();
      } else {
        if (timer) clearTimeout(timer);
        void run();
      }
    };
    document.addEventListener('visibilitychange', onVisibilityChange);
    void run();
    return () => {
      mounted = false;
      document.removeEventListener('visibilitychange', onVisibilityChange);
      if (timer) clearTimeout(timer);
      controller?.abort();
    };
  }, [enabled, fetcher, ms, revision]);

  return { data, error, loading: loading || (enabled && data === undefined && error === undefined), refresh: () => setRevision((value) => value + 1) };
}

function isVisible(): boolean {
  return document.visibilityState !== 'hidden';
}
