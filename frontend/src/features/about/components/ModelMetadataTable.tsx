import React from 'react';
import { useLocalized } from '../../../app/localeContext';
import { aboutContent } from '../../../content/about.content';
import { Chapter } from './Chapter';

export const ModelMetadataTable: React.FC = () => {
  const { modelMetadata } = useLocalized(aboutContent);

  return (
    <Chapter
      heading={modelMetadata.heading}
      subline={modelMetadata.subline}
    >
      <p className="text-lg sm:text-xl short:text-[17px] text-body leading-relaxed">{modelMetadata.description}</p>

      <table className="mt-8 w-full text-left border-t border-ink/80">
        <caption className="sr-only">{modelMetadata.heading}</caption>
        <thead className="sr-only">
          <tr>
            <th scope="col">{modelMetadata.parameterCol}</th>
            <th scope="col">{modelMetadata.valueCol}</th>
          </tr>
        </thead>
        <tbody>
          {modelMetadata.parameters.map((row, idx) => (
            <tr key={idx} className="border-b border-line align-top">
              <th scope="row" className="py-4 pr-6 w-[40%] text-base font-normal text-muted">
                {row.parameter}
              </th>
              <td className="tabular py-4 text-base font-medium text-ink break-words">
                {row.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Chapter>
  );
};
