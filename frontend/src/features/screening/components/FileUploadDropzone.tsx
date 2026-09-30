import React, { useRef, useState } from 'react';
import { Upload, FileImage, X } from 'lucide-react';
import { useLocalized } from '../../../app/localeContext';
import { screeningContent } from '../../../content/screening.content';
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
  const { upload } = useLocalized(screeningContent);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = (file: File) => {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError(upload.invalidType);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError(upload.fileTooLarge);
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
    e.target.value = '';
  };

  const openPicker = () => fileInputRef.current?.click();

  return (
    <div className={className}>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png, image/jpeg, image/jpg, image/webp"
        onChange={handleInputChange}
        className="hidden"
        aria-label={upload.chooseFileButton}
      />

      {selectedPreviewUrl ? (
        <div>
          <div>
            <div className="w-full aspect-square max-w-[560px] lg:max-w-[min(560px,max(260px,calc(100svh_-_280px)))] mx-auto bg-white border border-line-strong rounded-[10px] overflow-hidden flex items-center justify-center">
              <img
                src={selectedPreviewUrl}
                alt={upload.previewAlt}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <span className="text-sm text-aqua-deep font-medium flex items-center gap-2">
              <FileImage className="w-4 h-4" aria-hidden="true" />
              {upload.fileReadyText}
            </span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClear}
              leftIcon={<X className="w-4 h-4" />}
            >
              {upload.changeFileButton}
            </Button>
          </div>
        </div>
      ) : (
        <div>
          <div
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openPicker();
              }
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={openPicker}
            className={`w-full aspect-square max-w-[560px] lg:max-w-[min(560px,max(260px,calc(100svh_-_280px)))] mx-auto rounded-[10px] border-2 border-dashed p-8 text-center cursor-pointer transition-colors flex flex-col items-center justify-center ${
              dragOver
                ? 'border-iris bg-iris-wash'
                : 'border-line-strong bg-paper hover:border-iris'
            }`}
          >
            <span className="w-14 h-14 rounded-full bg-iris-wash flex items-center justify-center text-iris mb-5" aria-hidden="true">
              <Upload className="w-6 h-6" strokeWidth={1.75} />
            </span>

            <p className="font-medium text-ink text-lg max-w-[24ch]">
              {upload.dropzoneTitle}
            </p>
            <p className="mt-2 text-sm text-body max-w-[34ch] leading-relaxed">
              {upload.dropzoneDesc}
            </p>

            <span className="mt-6 inline-flex items-center min-h-11 px-5 rounded-md border border-iris text-iris text-[15px] font-medium">
              {upload.chooseFileButton}
            </span>

            {error && (
              <p className="mt-4 text-sm text-rose-ink font-medium" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
