import type { AppRoute } from '../app/routes';

export interface NavItemContent {
  id: string;
  label: string;
  path: AppRoute;
  isAction?: boolean;
}

export interface NavigationContent {
  brand: {
    title: string;
    tagline: string;
  };
  menuItems: NavItemContent[];
  footer: {
    brandDescription: string;
    navigationTitle: string;
    disclaimerTitle: string;
    disclaimerText: string;
    copyrightText: string;
  };
}

export interface HomeWorkflowStep {
  number: string;
  title: string;
  description: string;
}

export interface HomeBiomarker {
  id: 'circle' | 'meander' | 'spiral';
  name: string;
  category: string;
  description: string;
}

export interface HomeContent {
  hero: {
    badge: string;
    title: string;
    tagline: string;
    lead: string;
    primaryCta: string;
    secondaryCta: string;
  };
  workflow: {
    heading: string;
    subtitle: string;
    steps: HomeWorkflowStep[];
  };
  biomarkers: {
    heading: string;
    subtitle: string;
    items: HomeBiomarker[];
  };
  faqPreview: {
    heading: string;
    subtitle: string;
    seeAllCta: string;
  };
  ctaBanner: {
    heading: string;
    description: string;
    buttonText: string;
  };
}

export interface StepInstructionContent {
  stepNumber: number;
  modality: 'circle' | 'meander' | 'spiral';
  title: string;
  category: string;
  instructionText: string;
  canvasTip: string;
}

export interface ScreeningContent {
  preparation: {
    title: string;
    subtitle: string;
    guidelines: string[];
    startButtonText: string;
  };
  steps: Record<'circle' | 'meander' | 'spiral', StepInstructionContent>;
  report: {
    title: string;
    statusLabels: {
      healthy: string;
      healthyDesc: string;
      parkinson: string;
      parkinsonDesc: string;
    };
    probabilityHeading: string;
    breakdownHeading: string;
    disclaimerTitle: string;
    disclaimerBody: string;
    actions: {
      printPdf: string;
      restart: string;
    };
  };
}

export interface BenchmarkMetricRow {
  modality: string;
  accuracy: string;
  precision: string;
  recall: string;
  f1Score: string;
  rocAuc: string;
}

export interface ModelParameterRow {
  parameter: string;
  value: string;
}

export interface AboutContent {
  hero: {
    title: string;
    subtitle: string;
  };
  aiRationale: {
    heading: string;
    transferLearningText: string;
    lateFusionHeading: string;
    lateFusionText: string;
    formulaText: string;
  };
  modelMetadata: {
    heading: string;
    description: string;
    parameters: ModelParameterRow[];
    benchmarkHeading: string;
    benchmarkDescription: string;
    benchmarkMetrics: BenchmarkMetricRow[];
    recallNote: string;
  };
  datasetProvenance: {
    heading: string;
    datasetName: string;
    institutions: string[];
    citations: {
      authors: string;
      title: string;
      journal: string;
    }[];
    subjectStats: string;
    zeroLeakageProtocol: string;
  };
}

export interface FaqItemContent {
  id: string;
  question: string;
  answer: string;
}

export interface FaqCategory {
  id: string;
  title: string;
  description: string;
  items: FaqItemContent[];
}

export interface FaqContent {
  title: string;
  lead: string;
  categories: FaqCategory[];
}
