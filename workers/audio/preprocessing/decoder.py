from __future__ import annotations

import io

import librosa
import numpy as np


def decode_audio(audio_bytes: bytes, sample_rate: int = 16_000) -> np.ndarray:
	"""Decode uploaded audio bytes into a normalized mono waveform."""
	if not audio_bytes:
		raise ValueError("audio_bytes is empty")

	waveform, _ = librosa.load(io.BytesIO(audio_bytes), sr=sample_rate, mono=True)

	if waveform.size == 0:
		raise ValueError("decoded audio is empty")

	return waveform.astype(np.float32, copy=False)
