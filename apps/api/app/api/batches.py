import csv
import io
import json
import zipfile
from pathlib import Path
from uuid import uuid4
from app.schemas.batch import (
    BatchCreateResponse,
    BatchResultsResponse,
    BatchStatusResponse,
)
from fastapi import APIRouter, File, HTTPException, UploadFile, status

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


def _validate_manifest(manifest_bytes: bytes):
    try:
        text = manifest_bytes.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid manifest.csv: {exc}",
        )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="manifest.csv contains no rows.",
        )

    if "name" not in rows[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='manifest.csv must contain a "name" column.',
        )

    if "result_json" not in rows[0]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='manifest.csv must contain a "result_json" column.',
        )

    manifest = {}

    for row in rows:
        name = (row.get("name") or "").strip()

        if not name:
            continue

        result_json = (row.get("result_json") or "").strip()

        manifest[name] = result_json

    return manifest


@router.post("", response_model=BatchCreateResponse)
async def create_batch(file: UploadFile = File(...)):
    """
    Upload a ZIP containing:

        call1.ogg
        call2.ogg
        ...
        manifest.csv

    Audio files must be at the ZIP root.
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

    # We intentionally require manifest.csv at the root.
    manifest_name = "manifest.csv"

    if manifest_name not in members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ZIP must contain manifest.csv at the root.",
        )

    manifest = _validate_manifest(
        archive.read(manifest_name)
    )

    audio_files = {}

    for member in members:
        path = Path(member)

        # Ignore directories and manifest.
        if member.endswith("/") or member == manifest_name:
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

    audio_names = set(audio_files)
    manifest_names = set(manifest)

    missing_from_manifest = sorted(audio_names - manifest_names)
    missing_from_zip = sorted(manifest_names - audio_names)

    batch_id = str(uuid4())

    _batches[batch_id] = {
        "batch_id": batch_id,
        "status": "processing",
        "total": len(audio_files),
        "processed": 0,
        "files": {},
        "manifest": manifest,
    }

    # Every file is processed independently.
    for name, audio_bytes in audio_files.items():
        if name in missing_from_manifest:
            _batches[batch_id]["files"][name] = {
                "status": "error",
                "error": "Audio file is missing from manifest.csv.",
            }
            continue

        try:
            # TODO:
            # Pass audio_bytes into the actual AutoAce inference service.
            #
            # prediction = analyze_audio(audio_bytes)
            #
            # For now, mark the file as pending.

            _batches[batch_id]["files"][name] = {
                "status": "processing",
                "prediction": None,
            }

        except Exception as exc:
            _batches[batch_id]["files"][name] = {
                "status": "error",
                "error": str(exc),
            }

        _batches[batch_id]["processed"] += 1

    for name in missing_from_zip:
        _batches[batch_id]["files"][name] = {
            "status": "error",
            "error": "File listed in manifest.csv was not found in the ZIP.",
        }

    _batches[batch_id]["status"] = "completed"

    return {
        "batch_id": batch_id,
        "status": _batches[batch_id]["status"],
        "total": _batches[batch_id]["total"],
        "processed": _batches[batch_id]["processed"],
        "missing_from_manifest": missing_from_manifest,
        "missing_from_zip": missing_from_zip,
    }


@router.get("/{batch_id}", response_model=BatchStatusResponse)
async def get_batch(batch_id: str):
    batch = _batches.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found.",
        )

    return {
        "batch_id": batch["batch_id"],
        "status": batch["status"],
        "total": batch["total"],
        "processed": batch["processed"],
    }