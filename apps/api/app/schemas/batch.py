from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


BatchStatus = Literal[
    "processing",
    "completed",
    "completed_with_errors",
    "error",
]


FileStatus = Literal[
    "processing",
    "completed",
    "error",
]


class BatchCreateResponse(BaseModel):
    batch_id: str
    status: BatchStatus
    total: int = Field(ge=0)
    processed: int = Field(ge=0)

    missing_from_manifest: list[str] = []
    missing_from_zip: list[str] = []


class BatchStatusResponse(BaseModel):
    batch_id: str
    status: BatchStatus
    total: int = Field(ge=0)
    processed: int = Field(ge=0)
    files: dict[str, FileStatus] = {}
    results: list[dict] = []
    file_progress: dict[str, int] = {}
    current_file: Optional[str] = None
    current_progress: int = Field(ge=0, le=100)
    current_stage: str = "waiting"


class BatchFileError(BaseModel):
    name: str
    status: Literal["error"] = "error"
    error: str


class BatchFileProcessing(BaseModel):
    name: str
    status: Literal["processing"] = "processing"


class BatchFileResult(BaseModel):
    name: str
    status: Literal["completed"] = "completed"

    emotional_tone: Literal[
        "neutral",
        "satisfied",
        "frustrated",
        "upset",
        "distressed",
    ]

    emotional_intensity: Literal["low", "medium", "high"]

    background_noise_present: bool
    background_noise_type: str

    background_noise_severity: Literal[
        "none",
        "low",
        "medium",
        "high",
    ]

    audio_quality: Literal[
        "clear",
        "slightly_impaired",
        "severely_impaired",
    ]

    speaker_overlap_present: bool
    long_silence_present: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class BatchResultsResponse(BaseModel):
    batch_id: str
    results: list[Union[BatchFileResult, BatchFileError, BatchFileProcessing]]


class PredictionExport(BaseModel):
    """
    Exact prediction schema used for downloadable output.
    The original filename is preserved in `name`.
    """

    name: str

    emotional_tone: Literal[
        "neutral",
        "satisfied",
        "frustrated",
        "upset",
        "distressed",
    ]

    emotional_intensity: Literal[
        "low",
        "medium",
        "high",
    ]

    background_noise_present: bool
    background_noise_type: str
    background_noise_severity: Literal[
        "none",
        "low",
        "medium",
        "high",
    ]

    audio_quality: Literal[
        "clear",
        "slightly_impaired",
        "severely_impaired",
    ]

    speaker_overlap_present: bool
    long_silence_present: bool

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )