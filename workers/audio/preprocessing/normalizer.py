from __future__ import annotations

import numpy as np


def normalize_waveform(
	waveform: np.ndarray,
	target_peak: float = 0.95,
	minimum_peak: float = 1e-4,
) -> np.ndarray:
	"""Remove DC offset and normalize usable audio without amplifying silence."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	normalized = np.asarray(waveform, dtype=np.float32).copy()
	normalized -= np.mean(normalized)

	peak = float(np.max(np.abs(normalized)))
	if peak < minimum_peak:
		return normalized

	normalized *= target_peak / peak
	return np.clip(normalized, -1.0, 1.0).astype(np.float32, copy=False)
