import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { screeningContent } from '../../../content/screening.content';

/** The medical notice set as the report's footnote, not a SaaS alert box. */
export const ClinicalDisclaimerBox: React.FC = () => {
  const { report } = screeningContent;

  return (
    <aside className="print-break-avoid grid grid-cols-12 gap-x-6 gap-y-3 py-8 short:py-6" aria-labelledby="report-disclaimer-title">
      <h3
        id="report-disclaimer-title"
        className="col-span-12 lg:col-span-4 self-start flex items-center gap-2 text-base font-semibold text-amber-ink"
      >
        <ShieldAlert className="w-5 h-5 shrink-0" strokeWidth={1.75} aria-hidden="true" />
        {report.disclaimerTitle}
      </h3>
      <div className="col-span-12 lg:col-span-8">
        <p className="text-[15px] text-body leading-relaxed max-w-[72ch]">{report.disclaimerBody}</p>
        <p className="mt-3 text-[15px] font-medium text-ink leading-relaxed max-w-[72ch]">
          Langkah Lanjutan: Konsultasikan hasil pemeriksaan ini ke dokter spesialis saraf (neurolog) di fasilitas kesehatan terdekat untuk mendapatkan pemeriksaan klinis komprehensif.
        </p>
      </div>
    </aside>
  );
};
