from __future__ import annotations

from typing import Mapping

import librosa
import numpy as np


EMOTIONAL_TONES = (
	"neutral",
	"satisfied",
	"frustrated",
	"upset",
	"distressed",
)


def extract_emotion_features(waveform: np.ndarray, sample_rate: int) -> dict[str, float]:
	"""Extract interpretable prosody features used by the baseline classifier."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	rms = librosa.feature.rms(y=waveform)[0]
	rms_mean = float(np.mean(rms))
	rms_std = float(np.std(rms))
	rms_p95 = float(np.percentile(rms, 95))

	pitch, _, _ = librosa.pyin(
		waveform,
		fmin=librosa.note_to_hz("C2"),
		fmax=librosa.note_to_hz("C7"),
		sr=sample_rate,
	)
	voiced_pitch = pitch[np.isfinite(pitch)]
	pitch_mean = float(np.mean(voiced_pitch)) if voiced_pitch.size else 0.0
	pitch_std = float(np.std(voiced_pitch)) if voiced_pitch.size else 0.0

	onset_strength = librosa.onset.onset_strength(y=waveform, sr=sample_rate)
	tempo = float(librosa.feature.tempo(onset_envelope=onset_strength, sr=sample_rate)[0])
	zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y=waveform)))

	return {
		"energy": min(rms_mean * 8.0, 1.0),
		"energy_variability": min(rms_std * 12.0, 1.0),
		"peak_energy": min(rms_p95 * 8.0, 1.0),
		"pitch": min(pitch_mean / 300.0, 1.0),
		"pitch_variability": min(pitch_std / 100.0, 1.0),
		"speaking_rate": min(max((tempo - 70.0) / 120.0, 0.0), 1.0),
		"roughness": min(zero_crossing_rate * 10.0, 1.0),
	}


def classify_emotional_tone(features: Mapping[str, float]) -> tuple[str, float]:
	"""Map prosody features to the API tone enum and a confidence estimate."""
	energy = features.get("energy", 0.0)
	variability = features.get("energy_variability", 0.0)
	peak_energy = features.get("peak_energy", 0.0)
	pitch = features.get("pitch", 0.0)
	pitch_variability = features.get("pitch_variability", 0.0)
	speaking_rate = features.get("speaking_rate", 0.0)
	roughness = features.get("roughness", 0.0)

	distress = min(
		1.0,
		0.35 * pitch_variability
		+ 0.25 * variability
		+ 0.20 * speaking_rate
		+ 0.20 * roughness,
	)
	anger = min(
		1.0,
		0.35 * peak_energy
		+ 0.25 * pitch
		+ 0.20 * pitch_variability
		+ 0.20 * roughness,
	)
	frustration = min(
		1.0,
		0.40 * speaking_rate
		+ 0.25 * energy
		+ 0.20 * variability
		+ 0.15 * roughness,
	)
	satisfaction = min(
		1.0,
		0.45 * (1.0 - variability)
		+ 0.30 * (1.0 - roughness)
		+ 0.25 * (1.0 - speaking_rate),
	)

	scores = {
		"neutral": max(0.0, 1.0 - max(distress, anger, frustration, satisfaction) * 0.8),
		"satisfied": satisfaction,
		"frustrated": frustration,
		"upset": anger,
		"distressed": distress,
	}
	tone = max(scores, key=scores.get)
	confidence = round(max(0.0, min(1.0, scores[tone])), 2)
	return tone, confidence
