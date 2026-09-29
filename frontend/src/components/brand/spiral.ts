/**
 * Geometry for ParkinDraw's drawn-line emblem.
 * One Archimedean spiral that unwinds into a meander tail: the three test
 * patterns (circle, meander, spiral) expressed as a single continuous stroke.
 */
export interface Point {
  x: number;
  y: number;
}

export function spiralPoints(
  cx: number,
  cy: number,
  turns: number,
  startRadius: number,
  growth: number,
  steps = 260
): Point[] {
  const points: Point[] = [];
  const maxTheta = turns * Math.PI * 2;
  for (let i = 0; i <= steps; i++) {
    const theta = (i / steps) * maxTheta;
    const r = startRadius + growth * theta;
    points.push({ x: cx + r * Math.cos(theta), y: cy + r * Math.sin(theta) });
  }
  return points;
}

/**
 * The NewHandPD spiral template (ml/data/raw/HealthySpiral/sp1-H1.jpg):
 * an Archimedean spiral of ~2.5 turns, counter-clockwise on screen, starting
 * at the centre and ending on the left, level with the centre.
 * Measured on the 674px scan: r ≈ 52 + 18.5·θ (px), θ ∈ [-2.2, 5π].
 * `scale` maps scan pixels to the target coordinate space.
 */
export function newHandPdSpiralPoints(cx: number, cy: number, scale: number, steps = 320): Point[] {
  const start = -2.2;
  const end = 5 * Math.PI;
  const points: Point[] = [];
  for (let i = 0; i <= steps; i++) {
    const theta = start + ((end - start) * i) / steps;
    const r = (52 + 18.5 * theta) * scale;
    points.push({ x: cx + r * Math.cos(theta), y: cy - r * Math.sin(theta) });
  }
  return points;
}

export function meanderPoints(
  from: Point,
  length: number,
  amplitude: number,
  waves: number,
  angle: number,
  steps = 140
): Point[] {
  const points: Point[] = [];
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const along = t * length;
    // amplitude eases in so the tail leaves the spiral smoothly
    const across = Math.sin(t * waves * Math.PI * 2) * amplitude * Math.min(1, t * 3);
    points.push({
      x: from.x + along * cos - across * sin,
      y: from.y + along * sin + across * cos,
    });
  }
  return points;
}

export function toPath(points: Point[]): string {
  if (points.length === 0) return '';
  const [first, ...rest] = points;
  return (
    `M${first.x.toFixed(1)} ${first.y.toFixed(1)}` +
    rest.map((p) => `L${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join('')
  );
}

/** Deterministic pseudo-random jitter so the ink line reads as a human hand. */
export function jitter(points: Point[], amount: number, seed = 7): Point[] {
  let s = seed;
  const rand = () => {
    s = (s * 16807) % 2147483647;
    return s / 2147483647 - 0.5;
  };
  return points.map((p) => ({ x: p.x + rand() * amount, y: p.y + rand() * amount }));
}
