import React from 'react';
import { RotateCcw, Trash2, Eye, EyeOff } from 'lucide-react';
import { Button } from '../../../components/ui/Button';

export interface CanvasToolbarProps {
  strokeWidth: number;
  onStrokeWidthChange: (width: number) => void;
  canUndo: boolean;
  onUndo: () => void;
  onClear: () => void;
  showWatermark: boolean;
  onToggleWatermark: () => void;
}

export const CanvasToolbar: React.FC<CanvasToolbarProps> = ({
  strokeWidth,
  onStrokeWidthChange,
  canUndo,
  onUndo,
  onClear,
  showWatermark,
  onToggleWatermark,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2.5 p-3 bg-slate-100 border border-slate-200 rounded-lg text-xs sm:text-sm">
      {/* Stroke Width Selector */}
      <div className="flex items-center gap-1.5">
        <span className="text-slate-600 font-medium mr-1 hidden sm:inline">Ketebalan:</span>
        {[2, 3, 5].map((width) => (
          <button
            key={width}
            type="button"
            onClick={() => onStrokeWidthChange(width)}
            className={`px-2.5 py-1 rounded-md font-medium border cursor-pointer ${
              strokeWidth === width
                ? 'bg-teal-700 text-white border-teal-700 font-semibold'
                : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
            }`}
          >
            {width === 2 ? 'Tipis' : width === 3 ? 'Sedang' : 'Tebal'}
          </button>
        ))}
      </div>

      {/* Action Tools */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onToggleWatermark}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 cursor-pointer text-xs"
        >
          {showWatermark ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          <span>{showWatermark ? 'Sembunyikan Panduan' : 'Lihat Panduan'}</span>
        </button>

        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={!canUndo}
          onClick={onUndo}
          leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
        >
          Urungkan
        </Button>

        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={onClear}
          leftIcon={<Trash2 className="w-3.5 h-3.5 text-rose-600" />}
        >
          Hapus
        </Button>
      </div>
    </div>
  );
};
