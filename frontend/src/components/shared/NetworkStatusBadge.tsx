import React from 'react';
import { useBackendHealth } from '../../hooks/useBackendHealth';
import { useLocalized } from '../../app/localeContext';
import { uiContent } from '../../content/ui.content';

/** System status printed as a quiet caption line, not a chrome pill. */
export const NetworkStatusBadge: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { isOnline, isLoading } = useBackendHealth();
  const { backendStatus } = useLocalized(uiContent);

  const state =
    isLoading && isOnline === null ? 'checking' : isOnline ? 'online' : 'offline';

  const config = {
    checking: { dot: 'bg-muted', text: 'text-muted', label: backendStatus.checking },
    online: { dot: 'bg-aqua-rule', text: 'text-aqua-deep', label: backendStatus.online },
    offline: { dot: 'bg-rose-ink', text: 'text-rose-ink', label: backendStatus.offline },
  }[state];

  return (
    <span
      role="status"
      aria-live="polite"
      className={`inline-flex items-center gap-2 text-[13px] font-medium ${config.text} ${className}`}
    >
      <span className="relative flex w-2 h-2" aria-hidden="true">
        {state === 'online' && (
          <span className="absolute inset-0 rounded-full bg-aqua-rule opacity-40 motion-safe:animate-ping" />
        )}
        <span className={`relative w-2 h-2 rounded-full ${config.dot}`} />
      </span>
      {config.label}
    </span>
  );
};
