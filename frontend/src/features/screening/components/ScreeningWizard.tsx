import React, { useEffect, useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Printer, RefreshCw, PenTool, UploadCloud } from 'lucide-react';
import type { DrawingModality } from '../../../services/types';
import { screeningContent } from '../../../content/screening.content';
import { useScreeningSession } from '../hooks/useScreeningSession';
import type { InputMode } from '../types';
import { Button } from '../../../components/ui/Button';
import { Tabs } from '../../../components/ui/Tabs';
import { Alert } from '../../../components/ui/Alert';
import { Medallion } from '../../../components/brand/Medallion';
import { StepIndicator } from './StepIndicator';
import { DrawingInstructions } from './DrawingInstructions';
import { DigitalCanvas, type DigitalCanvasRef } from './DigitalCanvas';
import { FileUploadDropzone } from './FileUploadDropzone';
import { AnalysisLoadingView } from './AnalysisLoadingView';
import { ReportSummaryCard } from './ReportSummaryCard';
import { ModalityBreakdownGrid } from './ModalityBreakdownGrid';
import { ClinicalDisclaimerBox } from './ClinicalDisclaimerBox';

const modalityKeys: Record<number, DrawingModality> = {
  1: 'circle',
  2: 'meander',
  3: 'spiral',
};

export interface ScreeningWizardProps {
  /** Session header, shown only on the preparation step so later steps own the viewport. */
  header?: React.ReactNode;
}

export const ScreeningWizard: React.FC<ScreeningWizardProps> = ({ header }) => {
  const {
    state,
    startScreening,
    saveDrawing,
    nextStep,
    prevStep,
    submitSession,
    resetSession,
  } = useScreeningSession();

  const canvasRef = useRef<DigitalCanvasRef | null>(null);
  const [activeInputMode, setActiveInputMode] = useState<InputMode>('canvas');
  const [validationError, setValidationError] = useState<string | null>(null);

  // Open the report at its top so the verdict is the first thing read
  const hasReport = state.currentStep === 4 && Boolean(state.result);
  useEffect(() => {
    if (hasReport) window.scrollTo({ top: 0 });
  }, [hasReport]);

  const { preparation, steps } = screeningContent;
  const currentModality = modalityKeys[state.currentStep];
  const currentInstruction = currentModality ? steps[currentModality] : null;

  // Handle proceed to next step
  const handleProceedNext = async () => {
    if (!currentModality) return;
    setValidationError(null);
    let latestDrawing: { blob: Blob; thumbnailUrl: string; inputMode: InputMode } | null = null;

    if (activeInputMode === 'canvas') {
      if (!canvasRef.current) return;
      const exportResult = await canvasRef.current.exportDrawing();

      if (!exportResult || !canvasRef.current.hasDrawn) {
        setValidationError(
          'Harap buat goresan pada kanvas sebelum melanjutkan ke tahap berikutnya.'
        );
        return;
      }

      saveDrawing(
        currentModality,
        exportResult.blob,
        exportResult.dataUrl,
        'canvas'
      );
      latestDrawing = { blob: exportResult.blob, thumbnailUrl: exportResult.dataUrl, inputMode: 'canvas' };
    } else {
      const existing = state.drawings[currentModality];
      if (!existing.blob || !existing.thumbnailUrl) {
        setValidationError('Harap pilih berkas foto gambar terlebih dahulu.');
        return;
      }
    }

    if (state.currentStep === 3) {
      submitSession(latestDrawing ? { [currentModality]: latestDrawing } : undefined);
    } else {
      nextStep();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // State 0: Preparation / Tutorial
  if (state.currentStep === 0) {
    return (
      <>
        {header}
        <div className="grid grid-cols-12 gap-x-6 gap-y-12">
          <div className="col-span-12 lg:col-span-5">
            <h2 className="text-4xl sm:text-5xl font-medium tracking-[-0.03em] leading-[1.05] text-ink">
              {preparation.title}
            </h2>
            <p className="mt-5 text-lg sm:text-xl text-body leading-relaxed max-w-[44ch]">
              {preparation.subtitle}
            </p>

            <div className="mt-10 short:mt-6 flex items-center gap-3" aria-hidden="true">
              {(['circle', 'meander', 'spiral'] as const).map((pattern) => (
                <Medallion
                  key={pattern}
                  pattern={pattern}
                  className="w-20 sm:w-24 short:w-16 text-ink"
                />
              ))}
            </div>

            <Button
              type="button"
              size="lg"
              onClick={startScreening}
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="mt-10 short:mt-6 w-full sm:w-auto"
            >
              {preparation.startButtonText}
            </Button>
          </div>

          <ol className="col-span-12 lg:col-span-6 lg:col-start-7 border-t border-ink/80" aria-label="Instruksi Persiapan">
            {preparation.guidelines.map((text, idx) => (
              <li key={idx} className="flex items-start gap-5 py-5 sm:py-6 short:py-2.5 border-b border-line">
                <span className="tabular w-8 shrink-0 text-2xl font-medium tracking-[-0.03em] text-iris leading-none pt-0.5">
                  {idx + 1}
                </span>
                <span className="text-lg short:text-base text-ink leading-relaxed">{text}</span>
              </li>
            ))}
          </ol>
        </div>
      </>
    );
  }

  // State: Analyzing
  if (state.isAnalyzing) {
    return <AnalysisLoadingView />;
  }

  // State 4: Final Screening Report
  if (state.currentStep === 4 && state.result) {
    const thumbnails = {
      circle: state.drawings.circle.thumbnailUrl,
      meander: state.drawings.meander.thumbnailUrl,
      spiral: state.drawings.spiral.thumbnailUrl,
    };

    return (
      <div>
        {/* The report is the last step of the same session: all three steps read as done */}
        <div className="no-print">
          <StepIndicator currentStep={4} />
        </div>

        {/* Screen title on the same step as every other screen title (36 → 48px) */}
        <header className="mb-10 short:mb-6 flex flex-wrap items-end justify-between gap-x-8 gap-y-3">
          <div>
            <h2 className="text-4xl sm:text-5xl short:text-4xl font-medium tracking-[-0.03em] leading-[1.05] text-ink">
              Laporan Skrining Pola Parkinson
            </h2>
            <p className="mt-3 short:mt-2 text-lg sm:text-xl short:text-lg text-body">Hasil Evaluasi Karakteristik Goresan</p>
          </div>
          {/* Document meta, set as plain text so it prints and reads as a record */}
          <dl className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted tabular">
            <div className="flex gap-1.5">
              <dt>ID Sesi:</dt>
              <dd className="text-ink">{state.result.session_id}</dd>
            </div>
            <div className="flex gap-1.5">
              <dt>Waktu Selesai:</dt>
              <dd className="text-ink">{new Date(state.result.timestamp).toLocaleString('id-ID')}</dd>
            </div>
          </dl>
        </header>

        <ReportSummaryCard result={state.result} />
        <ModalityBreakdownGrid result={state.result} thumbnails={thumbnails} />
        <ClinicalDisclaimerBox />

        {/* Action Buttons */}
        {/* Phones: full-width stack, print first; wider screens: one row, left and right */}
        <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-6 border-t border-line no-print">
          <Button
            type="button"
            variant="outline"
            size="lg"
            onClick={resetSession}
            leftIcon={<RefreshCw className="w-4 h-4 shrink-0" />}
            className="!px-4 sm:!px-6 leading-tight"
          >
            Lakukan Skrining Baru
          </Button>

          <Button
            type="button"
            variant="primary"
            size="lg"
            onClick={() => window.print()}
            leftIcon={<Printer className="w-4 h-4 shrink-0" />}
            className="!px-4 sm:!px-6 leading-tight"
          >
            Cetak / Simpan Laporan (PDF)
          </Button>
        </div>
      </div>
    );
  }

  // States 1..3: Active Drawing Assessment
  return (
    <div>
      <StepIndicator currentStep={state.currentStep} />

      <div className="grid grid-cols-12 gap-x-6 lg:gap-x-12 gap-y-10 lg:gap-y-8">
        <div className="col-span-12 lg:col-span-5 lg:row-start-1">
          {currentInstruction && <DrawingInstructions instruction={currentInstruction} />}
        </div>

        <div className="col-span-12 lg:col-span-7 lg:col-start-6 lg:row-start-1 lg:row-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4 tight:mb-3">
            <Tabs
              activeTab={activeInputMode}
              onChange={(tab) => {
                setActiveInputMode(tab as InputMode);
                setValidationError(null);
              }}
              tabs={[
                {
                  id: 'canvas',
                  label: 'Kanvas Digital',
                  icon: <PenTool className="w-4 h-4" aria-hidden="true" />,
                },
                {
                  id: 'upload',
                  label: 'Unggah Foto Kertas',
                  icon: <UploadCloud className="w-4 h-4" aria-hidden="true" />,
                },
              ]}
            />
          </div>

          {activeInputMode === 'canvas' ? (
            <DigitalCanvas
              key={`canvas-${currentModality}`}
              ref={canvasRef}
              modality={currentModality}
            />
          ) : (
            <FileUploadDropzone
              selectedPreviewUrl={state.drawings[currentModality].thumbnailUrl}
              onFileSelect={(file, previewUrl) => {
                saveDrawing(currentModality, file, previewUrl, 'upload');
                setValidationError(null);
              }}
              onClear={() => {
                saveDrawing(currentModality, new Blob(), '', 'upload');
              }}
            />
          )}

          {(validationError || state.error) && (
            <div className="mt-5">
              <Alert type="error" title="Perhatian">
                {validationError || state.error}
              </Alert>
            </div>
          )}
        </div>

        {/* Step navigation: under the workspace on phones, under the instructions on laptops */}
        <nav
          aria-label="Navigasi Tahapan"
          className="col-span-12 lg:col-span-5 lg:row-start-2 lg:self-start flex flex-row items-center justify-between gap-3 pt-6 short:pt-4 border-t border-line"
        >
          {/* Back on the left, forward on the right, always on one row */}
          {state.currentStep > 1 ? (
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={prevStep}
              leftIcon={<ArrowLeft className="w-5 h-5 sm:w-4 sm:h-4" />}
              className="shrink-0 !px-4 sm:!px-5"
            >
              {/* Icon-only on phones so the forward action keeps a single line */}
              <span className="sr-only sm:not-sr-only">Kembali</span>
            </Button>
          ) : (
            <span aria-hidden="true" />
          )}

          <Button
            type="button"
            variant="primary"
            size="lg"
            onClick={handleProceedNext}
            rightIcon={<ArrowRight className="hidden sm:block w-5 h-5 shrink-0" />}
            className="flex-1 sm:flex-none min-w-0 !px-4 sm:!px-5 text-[15px] sm:text-base leading-tight"
          >
            {state.currentStep === 3
              ? 'Kirim & Analisis Seluruh Gambar'
              : 'Lanjut ke Pola Berikutnya'}
          </Button>
        </nav>
      </div>
    </div>
  );
};
