import pytest
from pydantic import ValidationError

from app.schemas.batch import BatchResultsResponse


def test_batch_results_response_rejects_null_fields():
    payload = {
        "batch_id": "batch-123",
        "results": [
            {
                "name": "call1.wav",
                "status": "completed",
                "emotional_tone": "neutral",
                "emotional_intensity": "low",
                "background_noise_present": False,
                "background_noise_type": "traffic",
                "background_noise_severity": "low",
                "audio_quality": "clear",
                "speaker_overlap_present": False,
                "long_silence_present": False,
                "confidence": 0.92,
            }
        ],
    }

    model = BatchResultsResponse(**payload)
    assert model.results[0].status == "completed"
    assert model.results[0].confidence == 0.92

    with pytest.raises(ValidationError):
        BatchResultsResponse(**{
            **payload,
            "results": [
                {
                    **payload["results"][0],
                    "background_noise_present": None,
                }
            ],
        })
