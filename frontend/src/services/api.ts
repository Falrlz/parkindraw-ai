import axios from 'axios';
import type {
  HealthResponse,
  ModelsInfoResponse,
  DrawingPrediction,
  SessionPredictionResponse,
  DrawingModality,
} from './types';

// In development, Vite server proxy handles /api and /health routing to http://127.0.0.1:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

/**
 * Check backend readiness and model loading status.
 */
export async function checkBackendHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
}

/**
 * Retrieve metadata, architecture specs, and benchmark scores of the loaded models.
 */
export async function getModelsInfo(): Promise<ModelsInfoResponse> {
  const response = await apiClient.get<ModelsInfoResponse>('/api/v1/models/info');
  return response.data;
}

/**
 * Execute single drawing inference for an individual modality.
 */
export async function predictSingleDrawing(
  file: Blob | File,
  modality: DrawingModality,
  threshold?: number
): Promise<{ prediction: DrawingPrediction; clinical_disclaimer: string; timestamp: string }> {
  const formData = new FormData();
  formData.append('file', file, `${modality}.png`);
  formData.append('modality', modality);
  if (threshold !== undefined) {
    formData.append('threshold', threshold.toString());
  }

  const response = await apiClient.post('/api/v1/predict/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

/**
 * Execute comprehensive 3-step screening session with Late Multi-Modal Fusion.
 */
export async function predictScreeningSession(
  circleBlob: Blob | File,
  meanderBlob: Blob | File,
  spiralBlob: Blob | File,
  threshold?: number
): Promise<SessionPredictionResponse> {
  const formData = new FormData();
  formData.append('circle_file', circleBlob, 'circle.png');
  formData.append('meander_file', meanderBlob, 'meander.png');
  formData.append('spiral_file', spiralBlob, 'spiral.png');
  if (threshold !== undefined) {
    formData.append('threshold', threshold.toString());
  }

  const response = await apiClient.post<SessionPredictionResponse>(
    '/api/v1/predict/session',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
    }
  );
  return response.data;
}
