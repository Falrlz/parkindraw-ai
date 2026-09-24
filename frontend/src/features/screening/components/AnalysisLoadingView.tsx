import React from 'react';
import { Activity } from 'lucide-react';

export const AnalysisLoadingView: React.FC = () => {
  return (
    <div
      role="status"
      aria-live="polite"
      className="p-12 text-center flex flex-col items-center justify-center max-w-md mx-auto bg-white border border-slate-200 rounded-xl"
    >
      <div className="w-14 h-14 rounded-full bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 mb-4 animate-pulse">
        <Activity className="w-7 h-7" aria-hidden="true" />
      </div>

      <h3 className="text-lg font-bold text-slate-900 mb-2">
        Memproses Analisis Pola Goresan
      </h3>

      <p className="text-sm text-slate-600 leading-relaxed mb-4">
        Model Computer Vision ResNet-18 sedang mengevaluasi keteraturan mikromotorik dari ketiga gambar dan menghitung Late Multi-Modal Fusion...
      </p>

      <span className="sr-only">Sedang memproses... Harap tunggu beberapa detik.</span>
      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
        <div className="bg-teal-700 h-full w-2/3 animate-pulse rounded-full" />
      </div>
    </div>
  );
};
