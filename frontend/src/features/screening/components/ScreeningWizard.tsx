import React, { useRef, useState } from 'react';
import { ArrowLeft, ArrowRight, Printer, RefreshCw, PenTool, UploadCloud, CheckCircle } from 'lucide-react';
import type { DrawingModality } from '../../../services/types';
import { screeningContent } from '../../../content/screening.content';
import { useScreeningSession } from '../hooks/useScreeningSession';
import type { InputMode } from '../types';
import { Button } from '../../../components/ui/Button';
import { Card, CardBody } from '../../../components/ui/Card';
import { Tabs } from '../../../components/ui/Tabs';
import { Alert } from '../../../components/ui/Alert';
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

export const ScreeningWizard: React.FC = () => {
  const {
    state,
    startScreening,
    saveDrawing,
    goToStep,
    nextStep,
    prevStep,
    submitSession,
    resetSession,
  } = useScreeningSession();

  const canvasRef = useRef<DigitalCanvasRef | null>(null);
  const [activeInputMode, setActiveInputMode] = useState<InputMode>('canvas');
  const [validationError, setValidationError] = useState<string | null>(null);

  const { preparation, steps } = screeningContent;
  const currentModality = modalityKeys[state.currentStep];
  const currentInstruction = currentModality ? steps[currentModality] : null;

  // Handle proceed to next step
  const handleProceedNext = async () => {
    if (!currentModality) return;
    setValidationError(null);

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
    } else {
      const existing = state.drawings[currentModality];
      if (!existing.blob || !existing.thumbnailUrl) {
        setValidationError('Harap pilih berkas foto gambar terlebih dahulu.');
        return;
      }
    }

    if (state.currentStep === 3) {
      submitSession();
    } else {
      nextStep();
    }
  };

  // State 0: Preparation / Tutorial
  if (state.currentStep === 0) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="border-slate-200">
          <CardBody className="p-6 sm:p-8">
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 mb-2">
              {preparation.title}
            </h2>
            <p className="text-sm sm:text-base text-slate-600 mb-6 leading-relaxed">
              {preparation.subtitle}
            </p>

            <ul className="space-y-3 mb-8" aria-label="Instruksi Persiapan">
              {preparation.guidelines.map((text, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm text-slate-700">
                  <CheckCircle className="w-5 h-5 text-teal-700 shrink-0 mt-0.5" aria-hidden="true" />
                  <span className="leading-snug">{text}</span>
                </li>
              ))}
            </ul>

            <Button
              type="button"
              size="lg"
              onClick={startScreening}
              rightIcon={<ArrowRight className="w-5 h-5" />}
              className="w-full sm:w-auto"
            >
              {preparation.startButtonText}
            </Button>
          </CardBody>
        </Card>
      </div>
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
      <div className="max-w-3xl mx-auto">
        <header className="mb-6">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-800 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200">
            Hasil Penapisan Multimodal
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-2">
            Laporan Skrining Neuromotorik
          </h1>
        </header>

        <ReportSummaryCard result={state.result} />
        <ModalityBreakdownGrid result={state.result} thumbnails={thumbnails} />
        <ClinicalDisclaimerBox />

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200 no-print">
          <Button
            type="button"
            variant="outline"
            onClick={resetSession}
            leftIcon={<RefreshCw className="w-4 h-4" />}
          >
            Lakukan Skrining Baru
          </Button>

          <Button
            type="button"
            variant="primary"
            onClick={() => window.print()}
            leftIcon={<Printer className="w-4 h-4" />}
          >
            Cetak / Simpan Laporan (PDF)
          </Button>
        </div>
      </div>
    );
  }

  // States 1..3: Active Drawing Assessment
  return (
    <div className="max-w-2xl mx-auto">
      <StepIndicator currentStep={state.currentStep} />

      {currentInstruction && (
        <DrawingInstructions instruction={currentInstruction} />
      )}

      {/* Input Mode Selector */}
      <div className="flex justify-center mb-4">
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
              icon: <PenTool className="w-4 h-4" />,
            },
            {
              id: 'upload',
              label: 'Unggah Foto Kertas',
              icon: <UploadCloud className="w-4 h-4" />,
            },
          ]}
        />
      </div>

      {/* Drawing / Upload Workspace */}
      <div className="mb-6">
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
      </div>

      {/* Validation or API Error Alerts */}
      {(validationError || state.error) && (
        <div className="mb-5">
          <Alert type="error" title="Perhatian">
            {validationError || state.error}
          </Alert>
        </div>
      )}

      {/* Bottom Step Navigation Bar */}
      <nav
        aria-label="Navigasi Tahapan"
        className="flex items-center justify-between gap-3 pt-4 border-t border-slate-200"
      >
        <div>
          {state.currentStep > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={prevStep}
              leftIcon={<ArrowLeft className="w-4 h-4" />}
            >
              Kembali
            </Button>
          )}
        </div>

        <Button
          type="button"
          variant="primary"
          onClick={handleProceedNext}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          {state.currentStep === 3
            ? 'Kirim & Analisis Seluruh Gambar'
            : 'Lanjut ke Pola Berikutnya'}
        </Button>
      </nav>
    </div>
  );
};
