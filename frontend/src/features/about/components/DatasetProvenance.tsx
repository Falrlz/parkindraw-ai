import React from 'react';
import { BookOpen } from 'lucide-react';
import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

export const DatasetProvenance: React.FC = () => {
  const { datasetProvenance } = aboutContent;

  return (
    <Chapter
      heading={datasetProvenance.heading}
      subline={datasetProvenance.datasetName}
    >
      {/* Subject counts, continued by how they were split: one paragraph, no callout box */}
      <p className="text-lg sm:text-xl short:text-[17px] text-body leading-relaxed max-w-[60ch]">
        {datasetProvenance.subjectStats} {datasetProvenance.zeroLeakageProtocol}
      </p>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-10">
        <div>
          <h3 className="text-base font-semibold text-ink pb-3 border-b border-ink/80">
            Institusi Peneliti Sumber
          </h3>
          <ul>
            {datasetProvenance.institutions.map((inst, idx) => (
              <li key={idx} className="py-4 border-b border-line text-base text-body leading-relaxed">
                {inst}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="flex items-center gap-2 text-base font-semibold text-ink pb-3 border-b border-ink/80">
            <BookOpen className="w-4 h-4" strokeWidth={1.75} aria-hidden="true" />
            Publikasi Ilmiah Rujukan
          </h3>
          <ul>
            {datasetProvenance.citations.map((cite, idx) => (
              <li key={idx} className="py-4 border-b border-line leading-relaxed">
                <p className="text-base font-medium text-ink">{cite.title}</p>
                <p className="mt-1 text-sm text-body">
                  {cite.authors} &bull; <span className="italic text-iris-deep">{cite.journal}</span>
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Chapter>
  );
};
