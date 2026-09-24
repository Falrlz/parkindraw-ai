import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';
import type { SessionPredictionResponse } from '../../../services/types';
import { screeningContent } from '../../../content/screening.content';
import { ProgressBar } from '../../../components/ui/ProgressBar';

export interface ReportSummaryCardProps {
  result: SessionPredictionResponse;
}

export const ReportSummaryCard: React.FC<ReportSummaryCardProps> = ({ result }) => {
  const { report } = screeningContent;
  const isParkinson = result.fusion_prediction === 'Parkinson';
  const percentage = result.fusion_probability * 100;

  return (
    <div
      className={`border-2 rounded-xl p-5 sm:p-6 mb-6 ${
        isParkinson
          ? 'bg-amber-50/60 border-amber-300'
          : 'bg-emerald-50/60 border-emerald-300'
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200/80">
        <div className="flex items-start gap-3">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
              isParkinson ? 'bg-amber-200 text-amber-900' : 'bg-emerald-200 text-emerald-900'
            }`}
            aria-hidden="true"
          >
            {isParkinson ? (
              <AlertTriangle className="w-6 h-6" />
            ) : (
              <CheckCircle2 className="w-6 h-6" />
            )}
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Hasil Penapisan Akhir
            </span>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 mt-0.5">
              {isParkinson
                ? report.statusLabels.parkinson
                : report.statusLabels.healthy}
            </h2>
            <p className="text-sm text-slate-700 mt-1 leading-relaxed max-w-xl">
              {isParkinson
                ? report.statusLabels.parkinsonDesc
                : report.statusLabels.healthyDesc}
            </p>
          </div>
        </div>

        <div className="text-left sm:text-right shrink-0">
          <span className="text-xs text-slate-500 block">Probabilitas Parkinson:</span>
          <span
            className={`text-3xl sm:text-4xl font-black ${
              isParkinson ? 'text-amber-900' : 'text-emerald-900'
            }`}
          >
            {percentage.toFixed(1)}%
          </span>
          <span className="text-xs text-slate-500 block mt-0.5">
            Ambang Batas: {(result.threshold * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Progress Bar Display */}
      <div className="pt-4">
        <ProgressBar
          value={percentage}
          label={report.probabilityHeading}
          color={isParkinson ? 'amber' : 'emerald'}
        />
      </div>

      {/* Metadata Session */}
      <div className="mt-4 pt-3 border-t border-slate-200/60 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span>ID Sesi: <code className="font-mono bg-white px-1.5 py-0.5 rounded border border-slate-200">{result.session_id.slice(0, 13)}...</code></span>
        <span>Waktu Selesai: {new Date(result.timestamp).toLocaleString('id-ID')}</span>
      </div>
    </div>
  );
};
