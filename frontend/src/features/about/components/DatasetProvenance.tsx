import React from 'react';
import { Database, BookOpen, ShieldCheck } from 'lucide-react';
import { aboutContent } from '../../../content/about.content';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';

export const DatasetProvenance: React.FC = () => {
  const { datasetProvenance } = aboutContent;

  return (
    <Card className="mb-8">
      <CardHeader className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700" aria-hidden="true">
          <Database className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-900">{datasetProvenance.heading}</h2>
          <p className="text-xs text-slate-500 font-medium">{datasetProvenance.datasetName}</p>
        </div>
      </CardHeader>

      <CardBody className="space-y-6">
        {/* Dataset Stats */}
        <p className="text-sm sm:text-base text-slate-700 leading-relaxed">
          {datasetProvenance.subjectStats}
        </p>

        {/* Zero Leakage Protocol */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1.5 text-teal-900 font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-teal-700" aria-hidden="true" />
            <span>Protokol Isolasi Pasien (Zero Clinical Leakage)</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            {datasetProvenance.zeroLeakageProtocol}
          </p>
        </div>

        {/* Institutions */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            Institusi Peneliti Sumber
          </h3>
          <ul className="space-y-1.5 text-xs sm:text-sm text-slate-700">
            {datasetProvenance.institutions.map((inst, idx) => (
              <li key={idx} className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-700" />
                <span>{inst}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Scientific Citations */}
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            <BookOpen className="w-4 h-4 text-slate-500" aria-hidden="true" />
            <span>Publikasi Ilmiah Rujukan</span>
          </div>
          <div className="space-y-2.5">
            {datasetProvenance.citations.map((cite, idx) => (
              <div key={idx} className="p-3 bg-white border border-slate-200 rounded-lg text-xs leading-relaxed">
                <p className="font-semibold text-slate-900">{cite.title}</p>
                <p className="text-slate-600 mt-0.5">{cite.authors} &bull; <span className="italic text-teal-800">{cite.journal}</span></p>
              </div>
            ))}
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
