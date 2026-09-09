from __future__ import annotations

from typing import Dict

import librosa
import numpy as np


def extract_acoustic_features(
	waveform: np.ndarray,
	sample_rate: int,
) -> Dict[str, float]:
	"""Extract shared acoustic measurements from a mono waveform."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	rms = librosa.feature.rms(y=waveform)[0]
	spectral_centroid = librosa.feature.spectral_centroid(
		y=waveform,
		sr=sample_rate,
	)[0]
	spectral_bandwidth = librosa.feature.spectral_bandwidth(
		y=waveform,
		sr=sample_rate,
	)[0]
	zero_crossing_rate = librosa.feature.zero_crossing_rate(y=waveform)[0]
	onset_strength = librosa.onset.onset_strength(y=waveform, sr=sample_rate)
	tempo = float(librosa.feature.tempo(onset_envelope=onset_strength, sr=sample_rate)[0])

	pitch, _, _ = librosa.pyin(
		waveform,
		fmin=librosa.note_to_hz("C2"),
		fmax=librosa.note_to_hz("C7"),
		sr=sample_rate,
	)
	voiced_pitch = pitch[np.isfinite(pitch)]

	return {
		"rms_mean": float(np.mean(rms)),
		"rms_std": float(np.std(rms)),
		"rms_p95": float(np.percentile(rms, 95)),
		"spectral_centroid": float(np.mean(spectral_centroid)),
		"spectral_bandwidth": float(np.mean(spectral_bandwidth)),
		"zero_crossing_rate": float(np.mean(zero_crossing_rate)),
		"tempo": tempo,
		"voiced_ratio": float(voiced_pitch.size / max(pitch.size, 1)),
		"pitch_mean": float(np.mean(voiced_pitch)) if voiced_pitch.size else 0.0,
		"pitch_std": float(np.std(voiced_pitch)) if voiced_pitch.size else 0.0,
	}


def estimate_speaker_overlap(features: Dict[str, float]) -> bool:
	"""Flag likely overlap only when voiced pitch variation is unusually broad."""
	return bool(
		features["voiced_ratio"] >= 0.35
		and features["pitch_std"] >= 85.0
		and features["rms_std"] >= 0.02
	)
