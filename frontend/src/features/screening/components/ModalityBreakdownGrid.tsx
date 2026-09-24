import React from 'react';
import type { SessionPredictionResponse, DrawingModality } from '../../../services/types';
import { Card, CardHeader, CardBody } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { ProgressBar } from '../../../components/ui/ProgressBar';

export interface ModalityBreakdownGridProps {
  result: SessionPredictionResponse;
  thumbnails: Record<DrawingModality, string | null>;
}

const modalityMeta: Record<DrawingModality, { title: string; category: string }> = {
  circle: { title: 'Circle (Lingkaran)', category: 'Pola Melingkar' },
  meander: { title: 'Meander (Gelombang)', category: 'Pola Sinusoidal' },
  spiral: { title: 'Spiral (Pilin)', category: 'Pola Berkelanjutan' },
};

export const ModalityBreakdownGrid: React.FC<ModalityBreakdownGridProps> = ({
  result,
  thumbnails,
}) => {
  const modalities: DrawingModality[] = ['circle', 'meander', 'spiral'];

  return (
    <div className="mb-6">
      <h3 className="text-base sm:text-lg font-bold text-slate-900 mb-3">
        Rincian Analisis Per Modalitas Gambar
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modalities.map((modality) => {
          const prediction = result.drawings[modality];
          const meta = modalityMeta[modality];
          const isParkinson = prediction.prediction === 'Parkinson';
          const parkinsonProb = prediction.probabilities.Parkinson * 100;
          const thumbnail = thumbnails[modality];

          return (
            <Card key={modality} className="border-slate-200">
              <CardHeader className="p-3.5 bg-slate-50">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {meta.category}
                  </span>
                  <Badge variant={isParkinson ? 'parkinson' : 'healthy'}>
                    {prediction.prediction}
                  </Badge>
                </div>
                <h4 className="font-bold text-slate-900 text-sm mt-1">{meta.title}</h4>
              </CardHeader>

              <CardBody className="p-3.5 flex flex-col gap-3">
                {/* Thumbnail Display */}
                <div className="w-full aspect-square bg-slate-50 border border-slate-200 rounded-lg overflow-hidden flex items-center justify-center p-2">
                  {thumbnail ? (
                    <img
                      src={thumbnail}
                      alt={`Goresan ${meta.title}`}
                      className="max-w-full max-h-full object-contain"
                    />
                  ) : (
                    <span className="text-xs text-slate-400">Tidak ada gambar</span>
                  )}
                </div>

                {/* Score Bar */}
                <div>
                  <ProgressBar
                    value={parkinsonProb}
                    label="Skor Probabilitas Parkinson"
                    color={isParkinson ? 'amber' : 'emerald'}
                  />
                  <div className="flex justify-between items-center text-xs text-slate-500 mt-1">
                    <span>Keyakinan: {(prediction.confidence * 100).toFixed(1)}%</span>
                    <span>Sehat: {(prediction.probabilities.Healthy * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
