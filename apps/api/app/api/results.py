import csv
import io
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .batches import _batches

router = APIRouter(prefix="/results", tags=["results"])
from app.schemas.batch import (
    BatchResultsResponse,
)

@router.get("/{batch_id}", response_model=BatchResultsResponse)
async def get_results(batch_id: str):
    batch = _batches.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    results = []

    for name, item in batch["files"].items():
        if item.get("status") == "error":
            results.append({
                "name": name,
                "status": "error",
                "error": item.get("error", "Unknown error"),
            })
            continue

        prediction = item.get("prediction")

        if prediction is None:
            results.append({
                "name": name,
                "status": "processing",
            })
            continue

        # Keep the actual prediction schema separate from UI metadata.
        results.append({
            "name": name,
            **prediction,
            "status": "completed",
        })

    return {
        "batch_id": batch_id,
        "results": results,
    }


@router.get("/{batch_id}/download")
async def download_results(
    batch_id: str,
    format: str = "json",
):
    batch = _batches.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found.",
        )

    predictions = []

    for name, item in batch["files"].items():
        prediction = item.get("prediction")

        if not prediction:
            continue

        # Downloaded prediction preserves the required schema.
        predictions.append({
            "name": name,
            **prediction,
        })

    if format.lower() == "json":
        content = json.dumps(
            predictions,
            indent=2,
        )

        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="autoace-{batch_id}.json"'
                )
            },
        )

    if format.lower() == "csv":
        output = io.StringIO()

        fields = [
            "name",
            "emotional_tone",
            "emotional_intensity",
            "background_noise_present",
            "background_noise_type",
            "background_noise_severity",
            "audio_quality",
            "speaker_overlap_present",
            "long_silence_present",
            "confidence",
        ]

        writer = csv.DictWriter(
            output,
            fieldnames=fields,
        )

        writer.writeheader()

        for prediction in predictions:
            writer.writerow(prediction)

        return StreamingResponse(
            io.BytesIO(
                output.getvalue().encode("utf-8")
            ),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="autoace-{batch_id}.csv"'
                )
            },
        )

    raise HTTPException(
        status_code=400,
        detail='format must be either "json" or "csv".',
    )