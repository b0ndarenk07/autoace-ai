from __future__ import annotations

import librosa
import numpy as np
from typing import Dict, Union


def detect_silence(
	waveform: np.ndarray,
	sample_rate: int,
	threshold_db: float = -40.0,
	minimum_duration_seconds: float = 1.0,
) -> Dict[str, Union[float, bool]]:
	"""Detect sustained low-energy regions in a decoded audio waveform."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	frame_length = min(2048, waveform.size)
	hop_length = max(frame_length // 4, 1)
	rms = librosa.feature.rms(
		y=waveform,
		frame_length=frame_length,
		hop_length=hop_length,
	)[0]

	reference = max(float(np.max(rms)), np.finfo(np.float32).eps)
	rms_db = librosa.amplitude_to_db(rms, ref=reference)
	silent_frames = rms_db <= threshold_db

	longest_run = 0
	current_run = 0
	for is_silent in silent_frames:
		if is_silent:
			current_run += 1
			longest_run = max(longest_run, current_run)
		else:
			current_run = 0

	longest_duration = longest_run * hop_length / sample_rate
	silent_duration = float(np.sum(silent_frames) * hop_length / sample_rate)
	audio_duration = waveform.size / sample_rate

	return {
		"long_silence_present": longest_duration >= minimum_duration_seconds,
		"longest_silence_seconds": round(longest_duration, 3),
		"silent_duration_seconds": round(silent_duration, 3),
		"silence_ratio": round(silent_duration / max(audio_duration, 1e-9), 3),
	}
