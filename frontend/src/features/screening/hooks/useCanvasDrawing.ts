import { useRef, useState, useCallback, useEffect } from 'react';

interface Point {
  x: number;
  y: number;
}

export function useCanvasDrawing(canvasWidth = 448, canvasHeight = 448) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [strokeWidth, setStrokeWidth] = useState<number>(3);
  const [hasDrawn, setHasDrawn] = useState<boolean>(false);
  const [history, setHistory] = useState<ImageData[]>([]);
  const lastPointRef = useRef<Point | null>(null);

  // Initialize canvas with white background
  const initCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setHistory([]);
    setHasDrawn(false);
  }, []);

  useEffect(() => {
    initCanvas();
  }, [initCanvas]);

  const saveState = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
    setHistory((prev) => [...prev.slice(-10), snapshot]); // keep last 10 states
  }, []);

  const getCoordinates = (e: React.PointerEvent<HTMLCanvasElement>): Point => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.setPointerCapture(e.pointerId);

    saveState();
    setIsDrawing(true);
    setHasDrawn(true);

    const point = getCoordinates(e);
    lastPointRef.current = point;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.beginPath();
    ctx.arc(point.x, point.y, strokeWidth / 2, 0, Math.PI * 2);
    ctx.fillStyle = '#0f172a';
    ctx.fill();
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const currentPoint = getCoordinates(e);
    const lastPoint = lastPointRef.current;

    if (lastPoint) {
      ctx.beginPath();
      ctx.moveTo(lastPoint.x, lastPoint.y);
      ctx.lineTo(currentPoint.x, currentPoint.y);
      ctx.strokeStyle = '#0f172a';
      ctx.lineWidth = strokeWidth;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();
    }

    lastPointRef.current = currentPoint;
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.releasePointerCapture(e.pointerId);
    }
    setIsDrawing(false);
    lastPointRef.current = null;
  };

  const handlePointerCancel = () => {
    setIsDrawing(false);
    lastPointRef.current = null;
  };

  const undo = () => {
    const canvas = canvasRef.current;
    if (!canvas || history.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const previousStates = [...history];
    const lastState = previousStates.pop();
    setHistory(previousStates);

    if (lastState) {
      ctx.putImageData(lastState, 0, 0);
      if (previousStates.length === 0) {
        setHasDrawn(false);
      }
    }
  };

  const clear = () => {
    initCanvas();
  };

  /**
   * Export the current canvas as a high-quality solid-white PNG blob
   */
  const exportToBlob = async (): Promise<{ blob: Blob; dataUrl: string } | null> => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const dataUrl = canvas.toDataURL('image/png');

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve({ blob, dataUrl });
        } else {
          resolve(null);
        }
      }, 'image/png');
    });
  };

  return {
    canvasRef,
    canvasWidth,
    canvasHeight,
    strokeWidth,
    setStrokeWidth,
    hasDrawn,
    isDrawing,
    canUndo: history.length > 0,
    handlePointerDown,
    handlePointerMove,
    handlePointerUp,
    handlePointerCancel,
    undo,
    clear,
    exportToBlob,
  };
}
