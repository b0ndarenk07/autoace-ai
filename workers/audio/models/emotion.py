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


def extract_emotion_features(
	waveform: np.ndarray,
	sample_rate: int,
	voiced_waveform: np.ndarray | None = None,
	vad_features: Mapping[str, float] | None = None,
) -> dict[str, float]:
	"""Extract interpretable prosody features used by the baseline classifier."""
	if waveform.size == 0:
		raise ValueError("waveform is empty")

	analysis_waveform = (
		voiced_waveform
		if voiced_waveform is not None and voiced_waveform.size > 0
		else waveform
	)
	vad_features = vad_features or {}

	rms = librosa.feature.rms(y=analysis_waveform)[0]
	rms_mean = float(np.mean(rms))
	rms_std = float(np.std(rms))
	rms_p95 = float(np.percentile(rms, 95))

	pitch, _, _ = librosa.pyin(
		analysis_waveform,
		fmin=librosa.note_to_hz("C2"),
		fmax=librosa.note_to_hz("C7"),
		sr=sample_rate,
	)
	voiced_pitch = pitch[np.isfinite(pitch)]
	pitch_mean = float(np.mean(voiced_pitch)) if voiced_pitch.size else 0.0
	pitch_std = float(np.std(voiced_pitch)) if voiced_pitch.size else 0.0

	onset_strength = librosa.onset.onset_strength(y=analysis_waveform, sr=sample_rate)
	tempo = float(librosa.feature.tempo(onset_envelope=onset_strength, sr=sample_rate)[0])
	zero_crossing_rate = float(
		np.mean(librosa.feature.zero_crossing_rate(y=analysis_waveform))
	)
	mfcc = librosa.feature.mfcc(y=analysis_waveform, sr=sample_rate, n_mfcc=13)
	spectrogram = np.abs(librosa.stft(analysis_waveform))
	normalized_spectrogram = spectrogram / np.maximum(
		np.sum(spectrogram, axis=0, keepdims=True),
		np.finfo(np.float32).eps,
	)
	spectral_flux = float(
		np.mean(
			np.sqrt(
				np.sum(np.square(np.diff(normalized_spectrogram, axis=1)), axis=0)
			)
		)
	)
	spectral_rolloff = librosa.feature.spectral_rolloff(
		y=analysis_waveform,
		sr=sample_rate,
		roll_percent=0.85,
	)[0]
	harmonic = librosa.effects.harmonic(analysis_waveform)
	residual = analysis_waveform - harmonic
	harmonic_power = float(np.sum(np.square(harmonic)))
	residual_power = float(np.sum(np.square(residual)))
	hnr_db = 10.0 * np.log10(
		harmonic_power / max(residual_power, np.finfo(np.float32).eps)
	)
	hnr = min(max((hnr_db + 10.0) / 30.0, 0.0), 1.0)

	voiced_pitch_range = (
		float(np.max(voiced_pitch) - np.min(voiced_pitch))
		if voiced_pitch.size
		else 0.0
	)
	pitch_slope = (
		float(np.polyfit(np.arange(voiced_pitch.size), voiced_pitch, 1)[0])
		if voiced_pitch.size >= 2
		else 0.0
	)
	segment_rate = min(
		vad_features.get("voice_segment_count", 0.0)
		/ max(vad_features.get("voiced_duration_seconds", 0.0), 1e-9)
		/ 4.0,
		1.0,
	)
	tempo_rate = min(max((tempo - 70.0) / 120.0, 0.0), 1.0)

	return {
		"energy": min(rms_mean * 8.0, 1.0),
		"energy_variability": min(rms_std * 12.0, 1.0),
		"peak_energy": min(rms_p95 * 8.0, 0.85),
		"pitch": min(pitch_mean / 300.0, 1.0),
		"pitch_variability": min(pitch_std / 100.0, 1.0),
		"speaking_rate": 0.6 * tempo_rate + 0.4 * segment_rate,
		"roughness": float(1.0 - np.exp(-zero_crossing_rate / 0.12)),
		"mfcc_mean": float(np.mean(mfcc)),
		"mfcc_std": float(np.std(mfcc)),
		"spectral_flux": spectral_flux,
		"spectral_rolloff": float(np.mean(spectral_rolloff) / (sample_rate / 2)),
		"hnr_db": hnr_db,
		"hnr": hnr,
		"voiced_pitch_range": voiced_pitch_range,
		"pitch_slope": pitch_slope,
		"voiced_ratio": vad_features.get("voiced_ratio", 0.0),
		"pause_ratio": vad_features.get("pause_ratio", 0.0),
		"mean_pause_seconds": vad_features.get("mean_pause_seconds", 0.0),
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
	hnr = features.get("hnr", 0.5)
	sustained_energy = min(energy, peak_energy)
	mfcc_variability = min(features.get("mfcc_std", 0.0) / 50.0, 1.0)
	spectral_flux = min(features.get("spectral_flux", 0.0), 1.0)
	spectral_rolloff = min(max(features.get("spectral_rolloff", 0.0), 0.0), 1.0)

	distress = min(
		1.0,
		0.30 * pitch_variability
		+ 0.25 * variability
		+ 0.20 * speaking_rate
		+ 0.15 * roughness
		+ 0.05 * mfcc_variability
		+ 0.05 * spectral_flux,
	)
	anger = min(
		1.0,
		0.40 * sustained_energy
		+ 0.15 * pitch
		+ 0.15 * pitch_variability
		+ 0.15 * roughness
		+ 0.10 * mfcc_variability
		+ 0.05 * spectral_flux,
	)
	frustration = min(
		1.0,
		0.40 * speaking_rate
		+ 0.25 * energy
		+ 0.20 * variability
		+ 0.10 * roughness
		+ 0.05 * spectral_flux,
	)
	satisfaction = min(
		1.0,
		0.45 * (1.0 - variability)
		+ 0.30 * (1.0 - roughness)
		+ 0.15 * (1.0 - speaking_rate)
		+ 0.05 * (1.0 - spectral_flux)
		+ 0.05 * (1.0 - spectral_rolloff),
	)
	
	# Pitch and spectral roughness are easily inflated by noisy recordings.
	# Require enough overall energy before they can dominate the tone.
	signal_strength = min(1.0, (energy + peak_energy) / 1.2)
	distress *= signal_strength
	anger *= signal_strength
	frustration *= signal_strength
	distress *= 0.8 + 0.2 * hnr
	anger *= 0.8 + 0.2 * hnr
	noise_dominance = roughness * (1.0 - hnr)
	anger *= max(0.0, 1.0 - 0.5 * noise_dominance)

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


def classify_emotional_intensity(features: Mapping[str, float]) -> str:
	"""Map normalized prosody features to a low, medium, or high intensity."""
	intensity_score = (
		0.35 * features.get("energy", 0.0)
		+ 0.25 * features.get("peak_energy", 0.0)
		+ 0.20 * features.get("pitch_variability", 0.0)
		+ 0.10 * features.get("speaking_rate", 0.0)
		+ 0.10 * features.get("roughness", 0.0)
	)

	if intensity_score >= 0.65:
		return "high"
	if intensity_score >= 0.35:
		return "medium"
	return "low"
