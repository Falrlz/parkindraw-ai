import React, { useState, forwardRef, useImperativeHandle } from 'react';
import type { DrawingModality } from '../../../services/types';
import { useCanvasDrawing } from '../hooks/useCanvasDrawing';
import { CanvasToolbar } from './CanvasToolbar';

export interface DigitalCanvasRef {
  exportDrawing: () => Promise<{ blob: Blob; dataUrl: string } | null>;
  clearDrawing: () => void;
  hasDrawn: boolean;
}

export interface DigitalCanvasProps {
  modality: DrawingModality;
  className?: string;
}

export const DigitalCanvas = forwardRef<DigitalCanvasRef, DigitalCanvasProps>(
  ({ modality, className = '' }, ref) => {
    const [showWatermark, setShowWatermark] = useState(true);

    const {
      canvasRef,
      canvasWidth,
      canvasHeight,
      strokeWidth,
      setStrokeWidth,
      hasDrawn,
      canUndo,
      handlePointerDown,
      handlePointerMove,
      handlePointerUp,
      handlePointerCancel,
      undo,
      clear,
      exportToBlob,
    } = useCanvasDrawing(448, 448);

    useImperativeHandle(
      ref,
      () => ({
        exportDrawing: exportToBlob,
        clearDrawing: clear,
        hasDrawn,
      }),
      [exportToBlob, clear, hasDrawn]
    );

    return (
      <div className={`flex flex-col gap-3 ${className}`}>
        <CanvasToolbar
          strokeWidth={strokeWidth}
          onStrokeWidthChange={setStrokeWidth}
          canUndo={canUndo}
          onUndo={undo}
          onClear={clear}
          showWatermark={showWatermark}
          onToggleWatermark={() => setShowWatermark((prev) => !prev)}
        />

        {/* Canvas Drawing Surface Container */}
        <div className="relative w-full aspect-square max-w-[448px] mx-auto border-2 border-slate-300 rounded-xl overflow-hidden bg-white shadow-xs touch-none select-none">
          {/* Watermark Template Overlay */}
          {showWatermark && (
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none opacity-20"
              viewBox="0 0 448 448"
              fill="none"
              stroke="#0f172a"
              strokeWidth="2"
              strokeDasharray="6 6"
              aria-hidden="true"
            >
              {modality === 'circle' && (
                <circle cx="224" cy="224" r="160" />
              )}
              {modality === 'meander' && (
                <path d="M 40 224 Q 90 80, 140 224 T 240 224 T 340 224 T 410 224" />
              )}
              {modality === 'spiral' && (
                <path d="M 224 224 C 224 210, 240 200, 250 210 C 265 225, 250 255, 230 260 C 195 270, 180 230, 185 200 C 195 150, 260 145, 290 165 C 335 195, 330 275, 290 315 C 235 370, 140 350, 105 290" />
              )}
            </svg>
          )}

          {/* Actual HTML5 Canvas */}
          <canvas
            ref={canvasRef}
            width={canvasWidth}
            height={canvasHeight}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerCancel}
            className="w-full h-full block cursor-crosshair drawing-surface"
            aria-label={`Kanvas gambar untuk pola ${modality}`}
          />
        </div>
      </div>
    );
  }
);

DigitalCanvas.displayName = 'DigitalCanvas';
