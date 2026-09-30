import React from 'react';
import { ArrowUpRight } from 'lucide-react';
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

      {/* Source register: the key sits beside each entry, and the printed address is the link itself */}
      <div className="mt-12">
        <h3 className="text-base font-semibold text-ink pb-3 border-b border-ink/80">
          {datasetProvenance.sourcesHeading}
        </h3>
        <ul>
          {datasetProvenance.sources.map((source) => (
            <li
              key={source.href}
              className="grid grid-cols-1 sm:grid-cols-[8rem_minmax(0,1fr)] gap-x-6 gap-y-1 py-6 border-b border-line"
            >
              <p className="text-sm text-muted sm:pt-1">{source.kind}</p>
              <div className="min-w-0">
                <p className="text-lg font-medium text-ink leading-snug max-w-[48ch]">{source.title}</p>
                <p className="mt-2 text-base text-body leading-relaxed max-w-[62ch]">{source.detail}</p>
                {source.meta && <p className="mt-1 text-sm text-muted italic">{source.meta}</p>}
                <a
                  href={source.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group mt-3 inline-flex items-start gap-1 text-sm font-medium text-iris-deep underline decoration-iris/40 underline-offset-4 hover:decoration-iris transition-colors break-all rounded-sm"
                >
                  <span>{source.hrefLabel}</span>
                  <ArrowUpRight
                    className="w-4 h-4 shrink-0 mt-px transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                    strokeWidth={1.75}
                    aria-hidden="true"
                  />
                  <span className="sr-only"> (membuka tab baru)</span>
                </a>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </Chapter>
  );
};
