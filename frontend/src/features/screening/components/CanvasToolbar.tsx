import React from 'react';
import { RotateCcw, Trash2, Eye, EyeOff } from 'lucide-react';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';

export interface CanvasToolbarProps {
  strokeWidth: number;
  onStrokeWidthChange: (width: number) => void;
  canUndo: boolean;
  onUndo: () => void;
  onClear: () => void;
  showWatermark: boolean;
  onToggleWatermark: () => void;
}

const toolButton =
  'inline-flex items-center justify-center lg:justify-start gap-2 min-h-12 tight:min-h-11 px-3 rounded-md text-sm sm:text-[15px] font-medium transition-colors cursor-pointer disabled:cursor-not-allowed disabled:text-line-strong';

/**
 * Phones: two rows above the sheet (pen weight, then actions).
 * Laptops: a vertical rail beside the sheet, so the sheet can use the full
 * viewport height. Every target is at least 48px tall for shaky hands.
 */
export const CanvasToolbar: React.FC<CanvasToolbarProps> = ({
  strokeWidth,
  onStrokeWidthChange,
  canUndo,
  onUndo,
  onClear,
  showWatermark,
  onToggleWatermark,
}) => {
  const { canvas } = useLocalized(screeningContent);

  return (
    <div className="flex flex-col gap-3 lg:gap-5 tight:gap-3 lg:w-44 lg:shrink-0">
      {/* Stroke Width Selector */}
      <div className="flex items-center lg:items-stretch lg:flex-col gap-3 lg:gap-2" role="group" aria-label={canvas.strokeLabel}>
        <span className="text-sm text-muted hidden sm:inline tight:hidden">{canvas.strokeLabel}:</span>
        <div className="grid grid-cols-3 lg:grid-cols-1 flex-1 p-1 bg-paper border border-line rounded-lg">
          {[2, 3, 5].map((width) => {
            const isActive = strokeWidth === width;
            return (
              <button
                key={width}
                type="button"
                aria-pressed={isActive}
                onClick={() => onStrokeWidthChange(width)}
                className={`${toolButton} ${isActive ? 'bg-ink-fill text-white' : 'text-body hover:text-ink hover:bg-ground'}`}
              >
                <span className="w-3 flex justify-center" aria-hidden="true">
                  <span className="rounded-full bg-current" style={{ width: width + 3, height: width + 3 }} />
                </span>
                {width === 2 ? canvas.strokeOptions.thin : width === 3 ? canvas.strokeOptions.medium : canvas.strokeOptions.thick}
              </button>
            );
          })}
        </div>
      </div>

      {/* Action Tools */}
      <div className="grid grid-cols-3 lg:grid-cols-1 gap-1 lg:pt-4 tight:pt-3 lg:border-t lg:border-line">
        <button
          type="button"
          onClick={onToggleWatermark}
          aria-pressed={showWatermark}
          className={`${toolButton} text-body hover:text-ink hover:bg-paper text-center lg:text-left leading-tight`}
        >
          {showWatermark ? <EyeOff className="w-4 h-4 shrink-0" aria-hidden="true" /> : <Eye className="w-4 h-4 shrink-0" aria-hidden="true" />}
          <span>{showWatermark ? canvas.hideGuide : canvas.showGuide}</span>
        </button>

        <button
          type="button"
          disabled={!canUndo}
          onClick={onUndo}
          className={`${toolButton} text-body hover:text-ink hover:bg-paper disabled:hover:bg-transparent`}
        >
          <RotateCcw className="w-4 h-4 shrink-0" aria-hidden="true" />
          {canvas.undo}
        </button>

        <button
          type="button"
          onClick={onClear}
          className={`${toolButton} text-rose-ink hover:bg-rose-wash`}
        >
          <Trash2 className="w-4 h-4 shrink-0" aria-hidden="true" />
          {canvas.clear}
        </button>
      </div>
    </div>
  );
};
