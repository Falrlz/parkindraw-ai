import React from 'react';
import { Alert } from '../../../components/ui/Alert';
import { screeningContent } from '../../../content/screening.content';

export const ClinicalDisclaimerBox: React.FC = () => {
  const { report } = screeningContent;

  return (
    <div className="mb-6">
      <Alert type="warning" title={report.disclaimerTitle}>
        <p className="text-slate-800">{report.disclaimerBody}</p>
        <p className="mt-2 text-xs font-semibold text-amber-900">
          Langkah Lanjutan: Konsultasikan hasil pemeriksaan ini ke dokter spesialis saraf (neurolog) di fasilitas kesehatan terdekat untuk mendapatkan pemeriksaan klinis komprehensif.
        </p>
      </Alert>
    </div>
  );
};
