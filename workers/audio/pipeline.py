from __future__ import annotations

import logging
from typing import Any, Callable

from workers.audio.features.silence import detect_silence
from workers.audio.features.quality import assess_audio_quality
from workers.audio.features.acoustic import (
    estimate_speaker_overlap,
    extract_acoustic_features,
)
from workers.audio.models.emotion import (
    classify_emotional_intensity,
    classify_emotional_tone,
    extract_emotion_features,
)
from workers.audio.preprocessing.decoder import decode_audio
from workers.audio.preprocessing.normalizer import normalize_waveform
from workers.audio.preprocessing.vad import (
    extract_non_speech_waveform,
    extract_vad_features,
)
from workers.audio.models.noise import (
    classify_noise,
    extract_noise_features,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ProgressCallback = Callable[[str, int, str], None]


def _report_progress(
    callback: ProgressCallback | None,
    filename: str,
    progress: int,
    stage: str,
) -> None:
    if callback is None:
        return
    try:
        callback(filename, progress, stage)
    except Exception:
        logger.debug("Progress callback failed", exc_info=True)


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


def analyze_audio(
    audio_bytes: bytes,
    filename: str,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    _report_progress(progress_callback, filename, 0, "starting")
    logger.info(
        "Starting audio analysis: filename=%s bytes=%d",
        filename,
        len(audio_bytes),
    )

    decoded_waveform = decode_audio(audio_bytes)
    _report_progress(progress_callback, filename, 10, "decoded audio")
    quality_result = assess_audio_quality(decoded_waveform, sample_rate=16_000)
    _report_progress(progress_callback, filename, 20, "assessed audio quality")
    waveform = normalize_waveform(decoded_waveform)
    voiced_waveform, vad_features = extract_vad_features(
        waveform,
        sample_rate=16_000,
    )
    background_waveform = extract_non_speech_waveform(
        waveform,
        sample_rate=16_000,
    )
    _report_progress(progress_callback, filename, 40, "completed voice activity detection")
    acoustic_features = extract_acoustic_features(waveform, sample_rate=16_000)
    _report_progress(progress_callback, filename, 55, "extracted acoustic features")
    logger.info(
        "Audio decoded: filename=%s samples=%d duration_seconds=%.2f",
        filename,
        waveform.size,
        waveform.size / 16_000,
    )
    if background_waveform.size:
        noise_features = extract_noise_features(
            background_waveform,
            sample_rate=16_000,
        )
        noise = classify_noise(noise_features)
    else:
        noise = {
            "present": False,
            "type": "",
            "severity": "none",
        }
    _report_progress(progress_callback, filename, 70, "classified background noise")
    silence = detect_silence(waveform, sample_rate=16_000)
    features = extract_emotion_features(
        waveform,
        sample_rate=16_000,
        voiced_waveform=voiced_waveform,
        vad_features=vad_features,
    )
    _report_progress(progress_callback, filename, 85, "extracted emotion features")
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
    intensity = classify_emotional_intensity(features)
    _report_progress(progress_callback, filename, 95, "classified emotional tone")

    quality = quality_result["quality"]

    logger.info(
        "Silence analysis completed: filename=%s long_silence=%s "
        "longest_seconds=%.2f silence_ratio=%.3f",
        filename,
        silence["long_silence_present"],
        silence["longest_silence_seconds"],
        silence["silence_ratio"],
    )

    logger.info(
        "Audio analysis completed: filename=%s tone=%s intensity=%s "
        "confidence=%.2f quality=%s rms=%s clipped_ratio=%s",
        filename,
        tone,
        intensity,
        confidence,
        quality,
        quality_result["rms"],
        quality_result["clipped_ratio"],
    )

    result = {
        "name": filename,
        "emotional_tone": tone,
        "emotional_intensity": intensity,
        "background_noise_present": noise["present"],
        "background_noise_type": noise["type"],
        "background_noise_severity": noise["severity"],
        "audio_quality": quality,
        "speaker_overlap_present": estimate_speaker_overlap(acoustic_features),
        "long_silence_present": silence["long_silence_present"],
        "confidence": confidence,
    }
    _report_progress(progress_callback, filename, 100, "completed")
    return result


def failsafe_analyze_audio(
    audio_bytes: bytes,
    filename: str,
    progress_callback: ProgressCallback | None = None,
) -> dict[str, Any]:
    """
    Return a valid prediction payload even when the real inference pipeline
    fails unexpectedly. This keeps the API contract stable during partial or
    degraded runtime conditions.
    """
    try:
        return analyze_audio(audio_bytes, filename, progress_callback)
    except Exception:
        _report_progress(progress_callback, filename, 100, "completed with fallback")
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
            "background_noise_type": "",
            "background_noise_severity": "none",
            "audio_quality": "clear",
            "speaker_overlap_present": False,
            "long_silence_present": False,
            "confidence": 0.0,
        }
