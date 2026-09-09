import io
import zipfile
from pathlib import Path
from uuid import uuid4

from app.schemas.batch import (
    BatchCreateResponse,
    BatchResultsResponse,
    BatchStatusResponse,
)
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from workers.audio.pipeline import failsafe_analyze_audio

router = APIRouter(prefix="/batches", tags=["batches"])

ALLOWED_AUDIO_EXTENSIONS = {
    ".ogg",
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
}

MAX_BATCH_SIZE = 250 * 1024 * 1024  # 250 MB


# Temporary in-memory storage.
# Replace with persistent storage/database/object storage for production.
_batches = {}


def _process_batch(batch_id: str, audio_files: dict[str, bytes]) -> None:
    """Analyze batch files independently after the upload response is sent."""
    batch = _batches[batch_id]

    for name, audio_bytes in audio_files.items():
        def report_progress(filename: str, progress: int, stage: str) -> None:
            batch["current_file"] = filename
            batch["current_progress"] = progress
            batch["current_stage"] = stage
            batch["file_progress"][filename] = progress

        try:
            prediction = failsafe_analyze_audio(audio_bytes, name, report_progress)
            batch["files"][name] = {
                "status": "completed",
                "prediction": prediction,
            }
        except Exception as exc:
            batch["files"][name] = {
                "status": "error",
                "error": str(exc),
            }

        batch["processed"] += 1
        batch["current_progress"] = 100

    batch["status"] = (
        "completed"
        if all(item["status"] == "completed" for item in batch["files"].values())
        else "completed_with_errors"
    )


@router.post("", response_model=BatchCreateResponse)
async def create_batch(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a ZIP containing:

        call1.ogg
        call2.wav
        ...

    Supported audio files must be at the ZIP root. Each file is analyzed
    independently using the same pipeline as the single-file endpoint.
    """

    filename = file.filename or ""

    if not filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch upload must be a ZIP file.",
        )

    contents = await file.read()

    if len(contents) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Batch exceeds the 250 MB upload limit.",
        )

    try:
        archive = zipfile.ZipFile(io.BytesIO(contents))
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid ZIP archive.",
        )

    members = archive.namelist()

    audio_files = {}

    for member in members:
        path = Path(member)

        # Ignore directories and nested files.
        if member.endswith("/"):
            continue

        # Audio must exist at ZIP root.
        if len(path.parts) != 1:
            continue

        if path.suffix.lower() not in ALLOWED_AUDIO_EXTENSIONS:
            continue

        audio_files[path.name] = archive.read(member)

    if not audio_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ZIP contains no supported audio files.",
        )

    batch_id = str(uuid4())

    _batches[batch_id] = {
        "batch_id": batch_id,
        "status": "processing",
        "total": len(audio_files),
        "processed": 0,
        "files": {},
        "file_progress": {},
        "current_file": None,
        "current_progress": 0,
        "current_stage": "waiting",
    }

    for name in audio_files:
        _batches[batch_id]["files"][name] = {
            "status": "processing",
            "prediction": None,
        }

    background_tasks.add_task(_process_batch, batch_id, audio_files)

    return {
        "batch_id": batch_id,
        "status": _batches[batch_id]["status"],
        "total": _batches[batch_id]["total"],
        "processed": _batches[batch_id]["processed"],
    }


@router.get("/{batch_id}", response_model=BatchStatusResponse)
async def get_batch(batch_id: str):
    batch = _batches.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found.",
        )

    results = []
    for name, item in batch["files"].items():
        if item["status"] == "completed":
            results.append({
                "name": name,
                **item["prediction"],
                "status": "completed",
            })
        elif item["status"] == "error":
            results.append({
                "name": name,
                "status": "error",
                "error": item.get("error", "Unknown error"),
            })
        else:
            results.append({
                "name": name,
                "status": "processing",
            })

    return {
        "batch_id": batch["batch_id"],
        "status": batch["status"],
        "total": batch["total"],
        "processed": batch["processed"],
        "files": {
            name: item["status"]
            for name, item in batch["files"].items()
        },
        "file_progress": batch["file_progress"],
        "current_file": batch["current_file"],
        "current_progress": batch["current_progress"],
        "current_stage": batch["current_stage"],
        "results": results,
    }