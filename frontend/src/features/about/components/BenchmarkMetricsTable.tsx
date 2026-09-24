import React from 'react';
import { BarChart3, CheckCircle } from 'lucide-react';
import { aboutContent } from '../../../content/about.content';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';

export const BenchmarkMetricsTable: React.FC = () => {
  const { modelMetadata } = aboutContent;

  return (
    <Card className="mb-8">
      <CardHeader className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700" aria-hidden="true">
          <BarChart3 className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900">{modelMetadata.benchmarkHeading}</h2>
          <p className="text-xs text-slate-500 font-medium">Evaluasi Partisi Pasien Terisolasi (Locked Partition)</p>
        </div>
      </CardHeader>

      <CardBody>
        <p className="text-sm text-slate-600 mb-4">{modelMetadata.benchmarkDescription}</p>

        <div className="overflow-x-auto border border-slate-200 rounded-lg mb-4">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-100/80 border-b border-slate-200 text-slate-700 font-semibold">
              <tr>
                <th scope="col" className="p-3 sm:p-3.5">Modalitas Uji</th>
                <th scope="col" className="p-3 sm:p-3.5 text-center">Akurasi</th>
                <th scope="col" className="p-3 sm:p-3.5 text-center">Presisi</th>
                <th scope="col" className="p-3 sm:p-3.5 text-center">Sensitivitas (Recall)</th>
                <th scope="col" className="p-3 sm:p-3.5 text-center">F1-Score</th>
                <th scope="col" className="p-3 sm:p-3.5 text-center">ROC-AUC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-800">
              {modelMetadata.benchmarkMetrics.map((row, idx) => {
                const isMacro = row.modality.includes('Macro');
                return (
                  <tr
                    key={idx}
                    className={
                      isMacro
                        ? 'bg-teal-50/60 font-semibold text-teal-950'
                        : idx % 2 === 0
                        ? 'bg-white'
                        : 'bg-slate-50/50'
                    }
                  >
                    <td className="p-3 sm:p-3.5 font-medium">{row.modality}</td>
                    <td className="p-3 sm:p-3.5 text-center font-mono">{row.accuracy}</td>
                    <td className="p-3 sm:p-3.5 text-center font-mono">{row.precision}</td>
                    <td className="p-3 sm:p-3.5 text-center font-mono font-bold text-teal-800">
                      {row.recall}
                    </td>
                    <td className="p-3 sm:p-3.5 text-center font-mono">{row.f1Score}</td>
                    <td className="p-3 sm:p-3.5 text-center font-mono font-bold text-teal-800">
                      {row.rocAuc}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="flex items-start gap-2.5 p-3.5 bg-teal-50 border border-teal-200 rounded-lg text-xs text-teal-950 leading-relaxed">
          <CheckCircle className="w-4 h-4 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
          <span><strong>Keunggulan Klinis:</strong> {modelMetadata.recallNote}</span>
        </div>
      </CardBody>
    </Card>
  );
};
