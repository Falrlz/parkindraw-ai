import React from 'react';
import { SectionContainer } from '../components/shared/SectionContainer';
import { PageHeader } from '../components/shared/PageHeader';
import { ScreeningWizard } from '../features/screening/components/ScreeningWizard';

export const ScreeningPage: React.FC = () => {
  return (
    <SectionContainer className="pt-8 sm:pt-12 pb-16">
      <PageHeader
        badge="Screening Workflow"
        title="Sesi Penapisan Neuromotorik"
        subtitle="Ikuti instruksi pengambilan tiga sampel pola goresan untuk mendapatkan analisis Late Multi-Modal Fusion berbasis model ResNet-18."
      />

      <ScreeningWizard />
    </SectionContainer>
  );
};
