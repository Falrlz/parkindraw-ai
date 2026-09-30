import React from 'react';
import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

export const BenchmarkMetricsTable: React.FC = () => {
  const { modelMetadata } = aboutContent;

  return (
    <Chapter
      heading={modelMetadata.benchmarkHeading}
      subline="Evaluasi Partisi Pasien Terisolasi (Locked Partition)"
    >
      <p className="text-lg sm:text-xl short:text-[17px] text-body leading-relaxed max-w-[62ch]">{modelMetadata.benchmarkDescription}</p>

      {/* Phones: each modality as a label/value block, recall first */}
      <ul className="sm:hidden mt-8 border-t border-ink/80">
        {modelMetadata.benchmarkMetrics.map((row, idx) => {
          const isMacro = row.modality.includes('Macro');
          const cells: [string, string, boolean][] = [
            ['Sensitivitas (Recall)', row.recall, true],
            ['ROC-AUC', row.rocAuc, true],
            ['Akurasi', row.accuracy, false],
            ['Presisi', row.precision, false],
            ['F1-Score', row.f1Score, false],
          ];
          return (
            <li key={idx} className={`py-5 border-b border-line ${isMacro ? 'bg-iris-wash -mx-5 px-5' : ''}`}>
              <p className={`text-base text-ink ${isMacro ? 'font-semibold' : 'font-medium'}`}>{row.modality}</p>
              <dl className="tabular mt-3 grid grid-cols-2 gap-x-4 gap-y-3">
                {cells.map(([label, value, key]) => (
                  <div key={label}>
                    <dt className={`text-sm ${key ? 'text-iris font-medium' : 'text-muted'}`}>{label}</dt>
                    <dd className={`text-lg ${key ? 'font-semibold text-iris-deep' : 'font-medium text-ink'}`}>{value}</dd>
                  </div>
                ))}
              </dl>
            </li>
          );
        })}
      </ul>

      {/* Every row shares the same 12px edge inset, so the washed macro row keeps its columns aligned */}
      <div className="hidden sm:block mt-8 overflow-x-auto">
        <table className="w-full min-w-[600px] text-left">
          <caption className="sr-only">{modelMetadata.benchmarkHeading}</caption>
          <thead>
            <tr className="border-b border-ink/80 text-sm text-muted">
              <th scope="col" className="py-3 pl-3 pr-4 font-normal">Modalitas Uji</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">Accuracy</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">Precision</th>
              <th scope="col" className="py-3 px-3 font-medium text-right text-iris">Recall</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">F1-Score</th>
              <th scope="col" className="py-3 px-3 font-medium text-right text-iris">ROC-AUC</th>
            </tr>
          </thead>
          <tbody className="tabular text-ink">
            {modelMetadata.benchmarkMetrics.map((row, idx) => {
              const isMacro = row.modality.includes('Macro');
              return (
                <tr
                  key={idx}
                  className={isMacro ? 'bg-iris-wash font-medium' : 'border-b border-line'}
                >
                  <th scope="row" className={`py-4 pl-3 pr-4 text-base ${isMacro ? 'font-semibold' : 'font-normal'}`}>
                    {row.modality}
                  </th>
                  <td className="py-4 px-3 text-right">{row.accuracy}</td>
                  <td className="py-4 px-3 text-right">{row.precision}</td>
                  <td className="py-4 px-3 text-right font-semibold text-iris-deep">{row.recall}</td>
                  <td className="py-4 px-3 text-right">{row.f1Score}</td>
                  <td className="py-4 px-3 text-right font-semibold text-iris-deep">{row.rocAuc}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Chapter>
  );
};
