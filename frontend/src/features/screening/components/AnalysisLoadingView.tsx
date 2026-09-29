import React from 'react';
import { Ribbon } from '../../../components/brand/Ribbon';

export const AnalysisLoadingView: React.FC = () => {
  return (
    <div
      role="status"
      aria-live="polite"
      className="max-w-[640px] mx-auto py-10 flex flex-col items-center text-center"
    >
      <Ribbon motion="loop" density={18} className="w-56 h-56 sm:w-64 sm:h-64" />

      <h2 className="mt-4 text-3xl sm:text-4xl font-medium tracking-[-0.03em] text-ink">
        Memproses Analisis Pola Goresan
      </h2>

      <p className="mt-4 text-lg text-body leading-relaxed max-w-[48ch]">
        Model Computer Vision ResNet-18 sedang mengevaluasi keteraturan mikromotorik dari ketiga gambar dan menghitung Late Multi-Modal Fusion...
      </p>

      <span className="sr-only">Sedang memproses... Harap tunggu beberapa detik.</span>
    </div>
  );
};
