import type { DrawingModality, SessionPredictionResponse } from '../../../services/types';

export type ScreeningStep = 0 | 1 | 2 | 3 | 4;
// 0: Tutorial & Kesiapan
// 1: Lingkaran (Circle)
// 2: Meander (Gelombang)
// 3: Spiral (Pilin)
// 4: Laporan Hasil (Report)

export type InputMode = 'canvas' | 'upload';

export interface DrawingItem {
  blob: Blob | null;
  thumbnailUrl: string | null;
  inputMode: InputMode;
}

export interface ScreeningSessionState {
  currentStep: ScreeningStep;
  drawings: Record<DrawingModality, DrawingItem>;
  isAnalyzing: boolean;
  result: SessionPredictionResponse | null;
  error: string | null;
}
