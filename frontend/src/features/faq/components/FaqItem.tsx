import React from 'react';
import type { FaqItemContent } from '../../../content/types';
import { Accordion } from '../../../components/ui/Accordion';

export interface FaqItemProps {
  item: FaqItemContent;
}

export const FaqItem: React.FC<FaqItemProps> = ({ item }) => {
  return (
    <Accordion id={item.id} title={item.question}>
      <p className="text-slate-700 leading-relaxed text-sm sm:text-base">
        {item.answer}
      </p>
    </Accordion>
  );
};
