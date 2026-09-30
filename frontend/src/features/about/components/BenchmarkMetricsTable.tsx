import React from 'react';
import { useLocalized } from '../../../app/localeContext';
import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

export const BenchmarkMetricsTable: React.FC = () => {
  const { modelMetadata } = useLocalized(aboutContent);

  return (
    <Chapter
      heading={modelMetadata.benchmarkHeading}
      subline={modelMetadata.benchmarkSubline}
    >
      <p className="text-lg sm:text-xl short:text-[17px] text-body leading-relaxed max-w-[62ch]">{modelMetadata.benchmarkDescription}</p>

      {/* Phones: each modality as a label/value block, recall first */}
      <ul className="sm:hidden mt-8 border-t border-ink/80">
        {modelMetadata.benchmarkMetrics.map((row, idx) => {
          const isMacro = row.modality.includes('Macro');
          const cells: [string, string, boolean][] = [
            [modelMetadata.tableHeaders.recall, row.recall, true],
            [modelMetadata.tableHeaders.rocAuc, row.rocAuc, true],
            [modelMetadata.tableHeaders.accuracy, row.accuracy, false],
            [modelMetadata.tableHeaders.precision, row.precision, false],
            [modelMetadata.tableHeaders.f1Score, row.f1Score, false],
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
              <th scope="col" className="py-3 pl-3 pr-4 font-normal">{modelMetadata.tableHeaders.modality}</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">{modelMetadata.tableHeaders.accuracy}</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">{modelMetadata.tableHeaders.precision}</th>
              <th scope="col" className="py-3 px-3 font-medium text-right text-iris">{modelMetadata.tableHeaders.recall}</th>
              <th scope="col" className="py-3 px-3 font-normal text-right">{modelMetadata.tableHeaders.f1Score}</th>
              <th scope="col" className="py-3 px-3 font-medium text-right text-iris">{modelMetadata.tableHeaders.rocAuc}</th>
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
