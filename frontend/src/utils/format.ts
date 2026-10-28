/**
 * Safely formats classification accuracy as a valid percentage.
 * Guarantees that accuracy is strictly bounded in [0.00%, 100.00%].
 * Prevents double-multiplication bugs (e.g. 230%) or regression loss leakage.
 */
export function formatAccuracy(val?: number | null): string {
  if (val === undefined || val === null || isNaN(val)) return 'N/A';
  // If value is a normalized fraction (0.0 to 1.0), convert to percentage
  let pct = val;
  if (val <= 1.0 && val >= 0.0) {
    pct = val * 100.0;
  }
  // Strictly enforce mathematical boundary [0.0, 100.0]%
  const bounded = Math.max(0.0, Math.min(100.0, pct));
  return `${bounded.toFixed(2)}%`;
}

export function formatMacroF1(val?: number | null): string {
  if (val === undefined || val === null || isNaN(val)) return 'N/A';
  let pct = val;
  if (val <= 1.0 && val >= 0.0) {
    pct = val * 100.0;
  }
  const bounded = Math.max(0.0, Math.min(100.0, pct));
  return `${bounded.toFixed(2)}%`;
}
