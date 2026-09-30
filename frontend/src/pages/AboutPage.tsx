import React from 'react';
import { SectionContainer } from '../components/shared/SectionContainer';
import { PageHeader } from '../components/shared/PageHeader';
import { Ribbon } from '../components/brand/Ribbon';
import { useLocalized } from '../app/localeContext';
import { aboutContent } from '../content/about.content';
import { TransferLearningChapter, LateFusionChapter } from '../features/about/components/ArchitectureOverview';
import { ModelMetadataTable } from '../features/about/components/ModelMetadataTable';
import { BenchmarkMetricsTable } from '../features/about/components/BenchmarkMetricsTable';
import { DatasetProvenance } from '../features/about/components/DatasetProvenance';

export const AboutPage: React.FC = () => {
  const { hero } = useLocalized(aboutContent);

  return (
    <SectionContainer className="pt-12 sm:pt-16 lg:pt-0">
      {/* Opening screen: page title and the first chapter fill exactly one viewport on laptops and monitors */}
      <div className="lg:min-h-[calc(100svh-72px)] lg:flex lg:flex-col lg:justify-center lg:py-10 short:py-6 squat:py-4">
        <PageHeader
          title={hero.title}
          subtitle={hero.subtitle}
          aside={
            <Ribbon
              density={20}
              className="w-full max-w-[360px] short:max-w-[230px] squat:max-w-[170px] ml-auto -mb-6 short:mb-0"
            />
          }
          className="!mb-0 !border-b-0"
        />
        <TransferLearningChapter className="lg:!pb-0" />
      </div>

      <LateFusionChapter />
      <ModelMetadataTable />
      <BenchmarkMetricsTable />
      <DatasetProvenance />
    </SectionContainer>
  );
};
