from __future__ import annotations

from typing import Dict, Union

import librosa
import numpy as np


QualityResult = Dict[str, Union[float, str]]


def assess_audio_quality(
	waveform: np.ndarray,
	sample_rate: int,
) -> QualityResult:
	"""Assess technical signal quality before normalization changes the level."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	absolute_waveform = np.abs(waveform)
	rms = float(np.sqrt(np.mean(np.square(waveform))))
	peak = float(np.max(absolute_waveform))
	clipped_ratio = float(np.mean(absolute_waveform >= 0.995))

	frame_rms = librosa.feature.rms(y=waveform)[0]
	dynamic_range = float(np.percentile(frame_rms, 95) - np.percentile(frame_rms, 10))
	spectral_flatness = float(np.mean(librosa.feature.spectral_flatness(y=waveform)))

	if rms < 0.005 or clipped_ratio >= 0.01:
		quality = "severely_impaired"
	elif rms < 0.02 or clipped_ratio >= 0.001 or dynamic_range < 0.001:
		quality = "slightly_impaired"
	else:
		quality = "clear"

	return {
		"quality": quality,
		"rms": round(rms, 5),
		"peak": round(peak, 5),
		"clipped_ratio": round(clipped_ratio, 5),
		"dynamic_range": round(dynamic_range, 5),
		"spectral_flatness": round(spectral_flatness, 5),
	}
