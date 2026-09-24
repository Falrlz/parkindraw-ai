import { useEffect, useState, useCallback } from 'react';
import { checkBackendHealth } from '../services/api';
import type { HealthResponse } from '../services/types';

export interface BackendHealthState {
  isOnline: boolean | null;
  isLoading: boolean;
  health: HealthResponse | null;
  error: string | null;
  refreshHealth: () => Promise<void>;
}

export function useBackendHealth(pollIntervalMs = 30000): BackendHealthState {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshHealth = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await checkBackendHealth();
      setHealth(data);
      setIsOnline(data.status === 'ok' && data.all_models_loaded);
      setError(null);
    } catch (err: unknown) {
      setIsOnline(false);
      setHealth(null);
      setError(err instanceof Error ? err.message : 'Backend unreachable');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();

    const interval = setInterval(refreshHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [refreshHealth, pollIntervalMs]);

  return {
    isOnline,
    isLoading,
    health,
    error,
    refreshHealth,
  };
}
