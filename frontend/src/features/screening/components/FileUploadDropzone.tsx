import React, { useRef, useState } from 'react';
import { Upload, FileImage, X } from 'lucide-react';
import { Button } from '../../../components/ui/Button';

export interface FileUploadDropzoneProps {
  onFileSelect: (file: File, previewUrl: string) => void;
  onClear: () => void;
  selectedPreviewUrl: string | null;
  className?: string;
}

export const FileUploadDropzone: React.FC<FileUploadDropzoneProps> = ({
  onFileSelect,
  onClear,
  selectedPreviewUrl,
  className = '',
}) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = (file: File) => {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Format berkas tidak didukung. Harap pilih gambar PNG, JPG, atau WebP.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Ukuran berkas terlalu besar (maksimal 10 MB).');
      return;
    }

    setError(null);
    const previewUrl = URL.createObjectURL(file);
    onFileSelect(file, previewUrl);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className={`w-full max-w-[448px] mx-auto ${className}`}>
      {selectedPreviewUrl ? (
        <div className="relative border-2 border-slate-300 rounded-xl overflow-hidden bg-white p-3 flex flex-col items-center">
          <div className="w-full aspect-square max-h-[380px] bg-slate-50 rounded-lg overflow-hidden flex items-center justify-center border border-slate-200">
            <img
              src={selectedPreviewUrl}
              alt="Pratinjau berkas yang diunggah"
              className="max-w-full max-h-full object-contain"
            />
          </div>

          <div className="mt-3 flex items-center justify-between w-full">
            <span className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <FileImage className="w-4 h-4 text-teal-700" />
              Berkas siap diproses
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClear}
              leftIcon={<X className="w-3.5 h-3.5" />}
            >
              Ganti Berkas
            </Button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors flex flex-col items-center justify-center min-h-[360px] ${
            dragOver
              ? 'border-teal-700 bg-teal-50/50'
              : 'border-slate-300 bg-white hover:border-slate-400 hover:bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/webp"
            onChange={handleInputChange}
            className="hidden"
            aria-label="Pilih berkas gambar untuk diunggah"
          />

          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 mb-4" aria-hidden="true">
            <Upload className="w-6 h-6" />
          </div>

          <p className="font-semibold text-slate-900 text-sm mb-1">
            Klik untuk memilih foto atau seret berkas ke sini
          </p>
          <p className="text-xs text-slate-500 mb-4 max-w-xs">
            Foto hasil gambar pada kertas putih polos. Format yang didukung: PNG, JPG, atau WebP (maks. 10 MB).
          </p>

          <Button type="button" size="sm" variant="secondary" className="pointer-events-none">
            Pilih Foto Kertas
          </Button>

          {error && (
            <p className="mt-3 text-xs text-rose-700 font-medium" role="alert">
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
