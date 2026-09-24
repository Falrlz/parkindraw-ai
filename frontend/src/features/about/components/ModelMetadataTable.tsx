import React from 'react';
import { Cpu } from 'lucide-react';
import { aboutContent } from '../../../content/about.content';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';

export const ModelMetadataTable: React.FC = () => {
  const { modelMetadata } = aboutContent;

  return (
    <Card className="mb-8">
      <CardHeader className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700" aria-hidden="true">
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900">{modelMetadata.heading}</h2>
          <p className="text-xs text-slate-500 font-medium">Parameter Operasional Model Runtime</p>
        </div>
      </CardHeader>

      <CardBody>
        <p className="text-sm text-slate-600 mb-4">{modelMetadata.description}</p>
        
        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-100/80 border-b border-slate-200 text-slate-700 font-semibold">
              <tr>
                <th scope="col" className="p-3 sm:p-3.5">Parameter Arsitektur</th>
                <th scope="col" className="p-3 sm:p-3.5">Nilai Spesifikasi Teknis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-slate-800">
              {modelMetadata.parameters.map((row, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                  <td className="p-3 sm:p-3.5 font-medium">{row.parameter}</td>
                  <td className="p-3 sm:p-3.5 font-mono text-xs text-slate-900">{row.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardBody>
    </Card>
  );
};
