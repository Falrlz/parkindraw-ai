import React from 'react';
import { SectionContainer } from '../components/shared/SectionContainer';
import { PageHeader } from '../components/shared/PageHeader';
import { faqContent } from '../content/faq.content';
import { FaqCategoryGroup } from '../features/faq/components/FaqCategoryGroup';

export const FaqPage: React.FC = () => {
  return (
    <SectionContainer className="pt-8 sm:pt-12 pb-16">
      <PageHeader
        badge="Edukasi & Transparansi"
        title={faqContent.title}
        subtitle={faqContent.lead}
      />

      <div className="max-w-3xl mx-auto">
        {faqContent.categories.map((category) => (
          <FaqCategoryGroup key={category.id} category={category} />
        ))}
      </div>
    </SectionContainer>
  );
};
