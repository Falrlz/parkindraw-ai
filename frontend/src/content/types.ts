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
  description: string;
}

export interface HomeContent {
  hero: {
    title: string;
    tagline: string;
  };
  explanation: {
    text: string;
  };
  workflow: {
    heading: string;
    steps: HomeWorkflowStep[];
  };
  biomarkers: {
    heading: string;
    items: HomeBiomarker[];
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
  tipsLabel?: string;
}

export interface ScreeningContent {
  pageTitle: string;
  preparation: {
    title: string;
    subtitle: string;
    guidelines: string[];
    startButtonText: string;
    instructionsLabel?: string;
  };
  steps: Record<'circle' | 'meander' | 'spiral', StepInstructionContent>;
  wizard: {
    progressLabel: string;
    navigationLabel: string;
    inputModes: {
      canvas: string;
      upload: string;
    };
    backButton: string;
    nextPatternButton: string;
    submitButton: string;
    validation: {
      drawRequired: string;
      fileRequired: string;
      allStepsRequired: string;
      analysisFailed: string;
      alertTitle: string;
    };
  };
  loading: {
    title: string;
    subtitle: string;
    srText: string;
  };
  canvas: {
    canvasAriaLabel: string;
    strokeLabel: string;
    strokeOptions: {
      thin: string;
      medium: string;
      thick: string;
    };
    showGuide: string;
    hideGuide: string;
    undo: string;
    clear: string;
  };
  upload: {
    dropzoneTitle: string;
    dropzoneDesc: string;
    chooseFileButton: string;
    changeFileButton: string;
    fileReadyText: string;
    previewAlt: string;
    invalidType: string;
    fileTooLarge: string;
  };
  report: {
    title: string;
    subtitle: string;
    metaLabels: {
      sessionId: string;
      completedAt: string;
    };
    statusLabels: {
      healthy: string;
      healthyShort: string;
      healthyDesc: string;
      parkinson: string;
      parkinsonShort: string;
      parkinsonDesc: string;
    };
    finalVerdictLabel: string;
    probabilityLabel: string;
    probabilityHeading: string;
    thresholdLabel: string;
    breakdownHeading: string;
    scoreLabel: string;
    noImageText: string;
    disclaimerTitle: string;
    disclaimerBody: string;
    followUpNotice: string;
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

export interface DatasetSource {
  /** Register key shown beside the entry, e.g. Dataset or Publikasi */
  kind: string;
  title: string;
  detail: string;
  meta?: string;
  href: string;
  /** The address as printed, so the source survives print and copy */
  hrefLabel: string;
}

export interface AboutContent {
  hero: {
    title: string;
    subtitle: string;
  };
  aiRationale: {
    heading: string;
    transferLearningSubline: string;
    transferLearningText: string;
    lateFusionHeading: string;
    lateFusionSubline: string;
    lateFusionText: string;
    formulaText: string;
  };
  modelMetadata: {
    heading: string;
    subline: string;
    description: string;
    parameters: ModelParameterRow[];
    parameterCol: string;
    valueCol: string;
    benchmarkHeading: string;
    benchmarkSubline: string;
    benchmarkDescription: string;
    tableHeaders: {
      modality: string;
      accuracy: string;
      precision: string;
      recall: string;
      f1Score: string;
      rocAuc: string;
    };
    benchmarkMetrics: BenchmarkMetricRow[];
    recallNote: string;
  };
  datasetProvenance: {
    heading: string;
    datasetName: string;
    sourcesHeading: string;
    sources: DatasetSource[];
    subjectStats: string;
    zeroLeakageProtocol: string;
  };
}

export interface FaqItemContent {
  id: string;
  question: string;
  answer: string;
}

export interface FaqContent {
  heading: string;
  items: FaqItemContent[];
}

export interface UiContent {
  settings: {
    title: string;
    theme: string;
    themeOptions: Record<'light' | 'dark' | 'system', string>;
    language: string;
  };
  nav: {
    mainLabel: string;
    mobileLabel: string;
    openMenu: string;
    closeMenu: string;
    skipToContent: string;
  };
  common: {
    openInNewTab: string;
  };
  backendStatus: {
    checking: string;
    online: string;
    offline: string;
  };
}
