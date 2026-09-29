/**
 * TypeScript interfaces synchronized with FastAPI backend schemas.
 */

export type DrawingModality = 'circle' | 'meander' | 'spiral';

export type PredictionClass = 'Healthy' | 'Parkinson';

export interface Probabilities {
  Healthy: number;
  Parkinson: number;
}

export interface DrawingPrediction {
  modality: DrawingModality;
  prediction: PredictionClass;
  prediction_code: number;
  confidence: number;
  probabilities: Probabilities;
}

export interface SinglePredictionResponse {
  prediction: DrawingPrediction;
  clinical_disclaimer: string;
  timestamp: string;
}

export interface SessionPredictionResponse {
  session_id: string;
  fusion_prediction: PredictionClass;
  fusion_prediction_code: number;
  fusion_probability: number;
  threshold: number;
  drawings: {
    circle: DrawingPrediction;
    meander: DrawingPrediction;
    spiral: DrawingPrediction;
  };
  clinical_disclaimer: string;
  timestamp: string;
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  version: string;
  environment: string;
  timestamp: string;
  device: string;
  models: {
    circle: boolean;
    meander: boolean;
    spiral: boolean;
  };
  all_models_loaded: boolean;
}

export interface ModalityBenchmark {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  test_samples: number;
}

export interface ModalityModelInfo {
  modality: string;
  architecture: string;
  input_size: number[];
  active_parameters: number;
  total_parameters: number;
  artifact_file: string;
  is_loaded: boolean;
  benchmark_metrics: ModalityBenchmark;
}

export interface ModelsInfoResponse {
  dataset: string;
  models: Record<DrawingModality, ModalityModelInfo>;
  macro_average_metrics: ModalityBenchmark;
}
