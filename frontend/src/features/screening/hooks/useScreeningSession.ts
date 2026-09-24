import { useState, useCallback } from 'react';
import type { DrawingModality } from '../../../services/types';
import { predictScreeningSession } from '../../../services/api';
import type { ScreeningSessionState, ScreeningStep, InputMode } from '../types';

const initialDrawingsState = {
  circle: { blob: null, thumbnailUrl: null, inputMode: 'canvas' as InputMode },
  meander: { blob: null, thumbnailUrl: null, inputMode: 'canvas' as InputMode },
  spiral: { blob: null, thumbnailUrl: null, inputMode: 'canvas' as InputMode },
};

export function useScreeningSession() {
  const [state, setState] = useState<ScreeningSessionState>({
    currentStep: 0,
    drawings: initialDrawingsState,
    isAnalyzing: false,
    result: null,
    error: null,
  });

  const startScreening = useCallback(() => {
    setState((prev) => ({ ...prev, currentStep: 1, error: null }));
  }, []);

  const saveDrawing = useCallback(
    (modality: DrawingModality, blob: Blob, thumbnailUrl: string, inputMode: InputMode) => {
      setState((prev) => ({
        ...prev,
        drawings: {
          ...prev.drawings,
          [modality]: { blob, thumbnailUrl, inputMode },
        },
      }));
    },
    []
  );

  const goToStep = useCallback((step: ScreeningStep) => {
    setState((prev) => ({ ...prev, currentStep: step }));
  }, []);

  const nextStep = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.min(4, prev.currentStep + 1) as ScreeningStep,
    }));
  }, []);

  const prevStep = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentStep: Math.max(0, prev.currentStep - 1) as ScreeningStep,
    }));
  }, []);

  const submitSession = useCallback(async () => {
    const { circle, meander, spiral } = state.drawings;

    if (!circle.blob || !meander.blob || !spiral.blob) {
      setState((prev) => ({
        ...prev,
        error: 'Harap selesaikan ketiga pola gambar (Lingkaran, Meander, dan Spiral) terlebih dahulu.',
      }));
      return;
    }

    try {
      setState((prev) => ({ ...prev, isAnalyzing: true, error: null }));

      const response = await predictScreeningSession(
        circle.blob,
        meander.blob,
        spiral.blob
      );

      setState((prev) => ({
        ...prev,
        isAnalyzing: false,
        result: response,
        currentStep: 4, // Pindah ke layar Laporan
      }));
    } catch (err: unknown) {
      setState((prev) => ({
        ...prev,
        isAnalyzing: false,
        error:
          err instanceof Error
            ? err.message
            : 'Gagal menganalisis sesi skrining. Pastikan backend aktif dan coba lagi.',
      }));
    }
  }, [state.drawings]);

  const resetSession = useCallback(() => {
    setState({
      currentStep: 0,
      drawings: initialDrawingsState,
      isAnalyzing: false,
      result: null,
      error: null,
    });
  }, []);

  return {
    state,
    startScreening,
    saveDrawing,
    goToStep,
    nextStep,
    prevStep,
    submitSession,
    resetSession,
  };
}
