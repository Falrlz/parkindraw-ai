# Metadata-Only Baseline — Findings

Interpretation of `metadata_baseline.json`. Regenerate both with:

```bash
uv run --extra data --extra train python scripts/evaluate_baseline.py
```

## Result

Subject-level ROC-AUC from four non-clinical features (`width`, `height`,
`aspect_ratio`, `file_size_kb`) — no pixel of the stroke is ever seen.

| Drawing | Mean AUC | Std | Per fold |
|---|---|---|---|
| circle | 0.761 | 0.107 | 0.912, 0.691, 0.681 |
| meander | 0.823 | 0.084 | 0.875, 0.704, 0.889 |
| spiral | **0.888** | 0.026 | 0.925, 0.864, 0.875 |

Evaluated on the same three folds, with the same subject-level aggregation the
CNN will use, so the numbers are directly comparable to model scores.

## Why the metadata separates the classes

A high baseline is ambiguous on its own, because file size grows for two very
different reasons. The `diagnostics` block separates them:

| Drawing | file_size ~ ink | file_size ~ pixel_count | ink ~ label |
|---|---|---|---|
| circle | +0.151 | **+0.998** | +0.372 |
| meander | **+0.581** | +0.119 | +0.357 |
| spiral | **+0.628** | +0.483 | +0.335 |

**Circle — pure acquisition artifact.** File size is almost perfectly explained
by pixel count (r = 0.998), and Parkinson circles were simply cropped larger:
mean width 268 px versus 165 px for Healthy. This has nothing to do with the
disease.

**Spiral and meander — partly genuine signal.** Image dimensions are nearly
equal between classes (spiral: 697 px vs 677 px, a 1.03x difference), yet mean
file size differs by 2.26x (372 KB vs 165 KB). File size correlates with ink
coverage instead (r ≈ 0.6).

That route is clinically plausible: tremor produces longer, jagged, overlapping
strokes, which means more ink, higher image entropy, and a larger JPEG. Ink
coverage is itself higher for Parkinson across all three drawings
(r ≈ +0.35 with the label).

## How to read this

**The baseline is not a direct proxy for what the CNN can exploit.**

- The CNN never sees `file_size_kb`
- Resizing to 224×224 **removes** the dimensional artifact, which is the main
  leak for circle
- What survives is JPEG compression texture (artifact) and ink coverage
  (legitimate signal)

So "the model must exceed 0.888" is a necessary check, not a sufficient one.
Passing it does not by itself prove clinical learning.

## The test that actually answers it

An ablation, not a comparison of numbers:

1. Train on the images as they are
2. Train on images re-encoded uniformly (same JPEG quality, same resolution)
3. Performance holds → the model reads stroke shape
4. Performance collapses → the model was reading the compression footprint

## Limits of these numbers

- **Wide fold spread.** With 53 development subjects, one validation fold holds
  roughly 18 people. Circle ranges from 0.681 to 0.912 across folds. Treat these
  as indicative, not precise. Spiral is the most stable (±0.026).
- **Correlation is not causation.** r = 0.63 does not prove that ink *causes*
  the file-size gap. The ink and scanner-setting contributions cannot be cleanly
  separated from this data alone.

## Actions

1. Include uniform re-encoding in preprocessing from the start (Phase 2, Step 1)
2. Plan the re-encode ablation as part of Phase 2, not as an afterthought
3. Record this as a dataset limitation in the model card — it constrains what
   any result on NewHandPD can claim
