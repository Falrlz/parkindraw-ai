import { useState, forwardRef, useImperativeHandle } from 'react';
import type { DrawingModality } from '../../../services/types';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';
import { useCanvasDrawing } from '../hooks/useCanvasDrawing';
import { CanvasToolbar } from './CanvasToolbar';
import { newHandPdSpiralPoints, toPath } from '../../../components/brand/spiral';

// NewHandPD spiral template fitted to the 448px canvas (scan 645px wide → 368px, centre offset as on paper)
const SPIRAL_GUIDE = toPath(newHandPdSpiralPoints(245, 250, 0.57));

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
    const { canvas, steps } = useLocalized(screeningContent);
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
      <div className={`flex flex-col lg:flex-row lg:items-start gap-4 lg:gap-5 ${className}`}>
        <CanvasToolbar
          strokeWidth={strokeWidth}
          onStrokeWidthChange={setStrokeWidth}
          canUndo={canUndo}
          onUndo={undo}
          onClear={clear}
          showWatermark={showWatermark}
          onToggleWatermark={() => setShowWatermark((prev) => !prev)}
        />

        {/* Canvas Drawing Surface: a measured sheet with registration corners */}
        <div className="flex-1 min-w-0">
          <div className="relative w-full aspect-square max-w-[560px] lg:max-w-[min(560px,max(260px,calc(100svh_-_280px)))] mx-auto lg:mx-0 bg-white border border-line-strong rounded-[10px] touch-none select-none">
            {(['top-2 left-2 border-t border-l', 'top-2 right-2 border-t border-r', 'bottom-2 left-2 border-b border-l', 'bottom-2 right-2 border-b border-r'] as const).map(
              (pos) => (
                <span key={pos} className={`absolute w-4 h-4 border-line-strong pointer-events-none ${pos}`} aria-hidden="true" />
              )
            )}

            {showWatermark && (
              <svg
                className="absolute inset-0 w-full h-full pointer-events-none"
                viewBox="0 0 448 448"
                fill="none"
                stroke="#6b5ce7"
                strokeOpacity="0.4"
                strokeWidth="2"
                strokeDasharray="6 7"
                strokeLinecap="round"
                aria-hidden="true"
              >
                {modality === 'circle' && <circle cx="224" cy="224" r="160" />}
                {modality === 'meander' && (
                  <path
                    d="M 44 400 V 48 H 410 V 308.4 H 133.6 V 136.9 H 317.7 V 227.9 H 231.6"
                    strokeLinejoin="round"
                  />
                )}
                {modality === 'spiral' && <path d={SPIRAL_GUIDE} />}
              </svg>
            )}

            <canvas
              ref={canvasRef}
              width={canvasWidth}
              height={canvasHeight}
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerCancel={handlePointerCancel}
              className="relative w-full h-full block rounded-[10px] cursor-crosshair drawing-surface mix-blend-multiply"
              aria-label={`${canvas.canvasAriaLabel}: ${steps[modality].title}`}
            />
          </div>
        </div>
      </div>
    );
  }
);

DigitalCanvas.displayName = 'DigitalCanvas';
