import React from 'react';
import { Network, Layers } from 'lucide-react';
import { aboutContent } from '../../../content/about.content';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';

export const ArchitectureOverview: React.FC = () => {
  const { aiRationale } = aboutContent;

  return (
    <div className="space-y-6 mb-8">
      {/* Transfer Learning Rationale */}
      <Card>
        <CardHeader className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700" aria-hidden="true">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">{aiRationale.heading}</h2>
            <p className="text-xs text-slate-500 font-medium">Deep Residual Learning & Frozen Backbone</p>
          </div>
        </CardHeader>
        <CardBody>
          <p className="text-sm sm:text-base text-slate-700 leading-relaxed">
            {aiRationale.transferLearningText}
          </p>
        </CardBody>
      </Card>

      {/* Late Fusion Section */}
      <Card>
        <CardHeader className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-700" aria-hidden="true">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">{aiRationale.lateFusionHeading}</h2>
            <p className="text-xs text-slate-500 font-medium">Penggabungan Probabilitas Independen</p>
          </div>
        </CardHeader>
        <CardBody className="space-y-4">
          <p className="text-sm sm:text-base text-slate-700 leading-relaxed">
            {aiRationale.lateFusionText}
          </p>
          <div className="bg-slate-100 p-4 rounded-lg border border-slate-200 text-center font-mono text-xs sm:text-sm font-semibold text-slate-800">
            {aiRationale.formulaText}
          </div>
        </CardBody>
      </Card>
    </div>
  );
};
