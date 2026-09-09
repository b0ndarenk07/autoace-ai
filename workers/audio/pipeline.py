from __future__ import annotations

import logging
from typing import Any

import numpy as np

from workers.audio.models.emotion import classify_emotional_tone, extract_emotion_features
from workers.audio.preprocessing.decoder import decode_audio


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _safe_int(value: Any, minimum: int = 0, maximum: int = 100) -> int:
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        numeric = minimum
    return max(minimum, min(maximum, numeric))


def _safe_float(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = minimum
    return max(minimum, min(maximum, numeric))


def analyze_audio(audio_bytes: bytes, filename: str) -> dict[str, Any]:
    logger.info(
        "Starting audio analysis: filename=%s bytes=%d",
        filename,
        len(audio_bytes),
    )

    waveform = decode_audio(audio_bytes)
    logger.info(
        "Audio decoded: filename=%s samples=%d duration_seconds=%.2f",
        filename,
        waveform.size,
        waveform.size / 16_000,
    )

    features = extract_emotion_features(waveform, sample_rate=16_000)
    logger.info(
        "Emotion features extracted: filename=%s energy=%.3f pitch=%.3f "
        "speaking_rate=%.3f roughness=%.3f",
        filename,
        features["energy"],
        features["pitch"],
        features["speaking_rate"],
        features["roughness"],
    )

    tone, confidence = classify_emotional_tone(features)
    intensity = "high" if confidence >= 0.75 else "medium" if confidence >= 0.45 else "low"

    energy = features["energy"]
    noise_present = features["roughness"] >= 0.45
    noise_severity = "high" if features["roughness"] >= 0.75 else "low" if noise_present else "none"

    quality = "severely_impaired" if energy < 0.01 else "slightly_impaired" if energy < 0.03 else "clear"

    logger.info(
        "Audio analysis completed: filename=%s tone=%s intensity=%s "
        "confidence=%.2f quality=%s",
        filename,
        tone,
        intensity,
        confidence,
        quality,
    )

    return {
        "name": filename,
        "emotional_tone": tone,
        "emotional_intensity": intensity,
        "background_noise_present": noise_present,
        "background_noise_type": "background noise" if noise_present else "none",
        "background_noise_severity": noise_severity,
        "audio_quality": quality,
        "speaker_overlap_present": False,
        "long_silence_present": bool(np.mean(np.abs(waveform) < 0.01) > 0.35),
        "confidence": confidence,
    }


def failsafe_analyze_audio(audio_bytes: bytes, filename: str) -> dict[str, Any]:
    """
    Return a valid prediction payload even when the real inference pipeline
    fails unexpectedly. This keeps the API contract stable during partial or
    degraded runtime conditions.
    """
    try:
        return analyze_audio(audio_bytes, filename)
    except Exception:
        logger.exception(
            "Audio analysis failed; returning failsafe result: filename=%s bytes=%d",
            filename,
            len(audio_bytes),
        )
        fallback_name = filename or "unknown.ogg"
        return {
            "name": fallback_name,
            "emotional_tone": "neutral",
            "emotional_intensity": "low",
            "background_noise_present": False,
            "background_noise_type": "none",
            "background_noise_severity": "none",
            "audio_quality": "clear",
            "speaker_overlap_present": False,
            "long_silence_present": False,
            "confidence": 0.0,
        }
