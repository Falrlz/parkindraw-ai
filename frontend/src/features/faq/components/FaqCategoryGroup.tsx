import React from 'react';
import type { FaqCategory } from '../../../content/types';
import { FaqItem } from './FaqItem';

export interface FaqCategoryGroupProps {
  category: FaqCategory;
}

export const FaqCategoryGroup: React.FC<FaqCategoryGroupProps> = ({ category }) => {
  return (
    <section aria-labelledby={`cat-${category.id}`} className="mb-8">
      <header className="mb-3">
        <h2 id={`cat-${category.id}`} className="text-lg sm:text-xl font-bold text-slate-900">
          {category.title}
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          {category.description}
        </p>
      </header>

      <div className="space-y-3">
        {category.items.map((item) => (
          <FaqItem key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
};
