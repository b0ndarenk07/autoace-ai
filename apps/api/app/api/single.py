from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from workers.audio.pipeline import failsafe_analyze_audio

router = APIRouter(prefix="/single", tags=["single"])

ALLOWED_EXTENSIONS = {
    ".ogg",
    ".wav",
}


@router.post("")
async def analyze_single_call(
    file: UploadFile = File(...),
):
    """
    Analyze one production call.
    Input: file.ogg or file.wav - Audio file in .ogg or .wav format.
    Output: Exact AutoAce prediction schema.
    """

    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .ogg and .wav audio files are currently supported.",
        )

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded audio file is empty.",
        )

    prediction = failsafe_analyze_audio(audio_bytes, filename)
    return prediction