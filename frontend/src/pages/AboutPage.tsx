import React from 'react';
import { SectionContainer } from '../components/shared/SectionContainer';
import { PageHeader } from '../components/shared/PageHeader';
import { aboutContent } from '../content/about.content';
import { ArchitectureOverview } from '../features/about/components/ArchitectureOverview';
import { ModelMetadataTable } from '../features/about/components/ModelMetadataTable';
import { BenchmarkMetricsTable } from '../features/about/components/BenchmarkMetricsTable';
import { DatasetProvenance } from '../features/about/components/DatasetProvenance';

export const AboutPage: React.FC = () => {
  const { hero } = aboutContent;

  return (
    <SectionContainer className="pt-8 sm:pt-12 pb-16">
      <PageHeader
        badge="Metodologi & Arsitektur"
        title={hero.title}
        subtitle={hero.subtitle}
      />

      <div className="max-w-4xl mx-auto space-y-2">
        <ArchitectureOverview />
        <ModelMetadataTable />
        <BenchmarkMetricsTable />
        <DatasetProvenance />
      </div>
    </SectionContainer>
  );
};
