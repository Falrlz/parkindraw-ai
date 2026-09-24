import React from 'react';
import { useBackendHealth } from '../../hooks/useBackendHealth';

export const NetworkStatusBadge: React.FC = () => {
  const { isOnline, isLoading } = useBackendHealth();

  if (isLoading && isOnline === null) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
        <span className="w-2 h-2 rounded-full bg-slate-400" />
        Memeriksa Sistem...
      </span>
    );
  }

  if (isOnline) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
        <span className="w-2 h-2 rounded-full bg-emerald-600" />
        Backend Online
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-50 text-rose-800 border border-rose-200">
      <span className="w-2 h-2 rounded-full bg-rose-600" />
      Backend Offline
    </span>
  );
};
