from __future__ import annotations

import librosa
import numpy as np


def extract_vad_features(
	waveform: np.ndarray,
	sample_rate: int,
	top_db: float = 30.0,
) -> tuple[np.ndarray, dict[str, float]]:
	"""Return VAD-positive samples and basic speech/pause measurements."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	hop_length = 256
	intervals = librosa.effects.split(
		waveform,
		top_db=top_db,
		frame_length=2048,
		hop_length=hop_length,
	)
	total_duration = waveform.size / sample_rate

	if intervals.size == 0:
		return np.empty(0, dtype=waveform.dtype), {
			"voiced_ratio": 0.0,
			"voiced_duration_seconds": 0.0,
			"voice_segment_count": 0.0,
			"pause_ratio": 1.0,
			"mean_pause_seconds": total_duration,
		}

	voiced_parts = [waveform[start:end] for start, end in intervals]
	voiced_waveform = np.concatenate(voiced_parts)
	segment_durations = (intervals[:, 1] - intervals[:, 0]) / sample_rate
	voiced_duration = float(np.sum(segment_durations))
	pauses = (intervals[1:, 0] - intervals[:-1, 1]) / sample_rate
	mean_pause = float(np.mean(pauses)) if pauses.size else 0.0

	return voiced_waveform, {
		"voiced_ratio": min(voiced_duration / max(total_duration, 1e-9), 1.0),
		"voiced_duration_seconds": voiced_duration,
		"voice_segment_count": float(intervals.shape[0]),
		"pause_ratio": max(0.0, 1.0 - voiced_duration / max(total_duration, 1e-9)),
		"mean_pause_seconds": mean_pause,
	}


def extract_non_speech_waveform(
	waveform: np.ndarray,
	sample_rate: int,
	top_db: float = 30.0,
) -> np.ndarray:
	"""Return samples outside VAD-positive intervals for noise analysis."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	intervals = librosa.effects.split(
		waveform,
		top_db=top_db,
		frame_length=2048,
		hop_length=256,
	)
	if intervals.size == 0:
		return waveform

	speech_mask = np.zeros(waveform.size, dtype=bool)
	for start, end in intervals:
		speech_mask[start:end] = True

	return waveform[~speech_mask]
