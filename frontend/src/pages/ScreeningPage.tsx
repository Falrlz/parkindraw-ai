import React from 'react';
import { SectionContainer } from '../components/shared/SectionContainer';
import { ScreeningWizard } from '../features/screening/components/ScreeningWizard';

export const ScreeningPage: React.FC = () => {
  return (
    <SectionContainer className="pt-10 sm:pt-14 short:pt-6 short:pb-12 tight:pt-4 tight:pb-6 lg:min-h-[calc(100svh-72px)] lg:flex lg:flex-col lg:justify-center">
      {/* Page title kept for screen readers; the wizard's own headings lead visually */}
      <h1 className="sr-only">Sesi Penapisan Neuromotorik</h1>
      <ScreeningWizard />
    </SectionContainer>
  );
};
