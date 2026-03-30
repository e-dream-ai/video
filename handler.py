from collections.abc import Callable, Mapping
from typing import Any
from uuid import UUID

import runpod

from utils.process_filmstrip import run_video_filmstrip
from utils.process_image import run_image_ingestion
from utils.process_md5 import run_video_md5
from utils.process_video import run_video_ingestion

ALLOWED_VIDEO_TYPES = frozenset(
    {
        "mp4",
        "avi",
        "mov",
        "wmv",
        "mkv",
        "flv",
        "mpeg",
        "webm",
        "ogv",
        "3gp",
        "3g2",
        "h264",
        "hevc",
        "divx",
        "xvid",
        "avchd",
    }
)
ALLOWED_IMAGE_TYPES = frozenset(
    {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "tiff",
        "svg",
        "ico",
        "heif",
        "heic",
    }
)
SUPPORTED_JOB_TYPES = ("video", "image", "md5", "filmstrip")
JobRunner = Callable[[dict[str, str]], None]
JOB_RUNNERS: dict[str, JobRunner] = {
    "video": run_video_ingestion,
    "image": run_image_ingestion,
    "md5": run_video_md5,
    "filmstrip": run_video_filmstrip,
}


def _is_valid_uuid(value: str) -> bool:
    """Return whether the provided value is a valid UUID string."""
    try:
        UUID(value)
    except (TypeError, ValueError):
        return False
    return True


def _normalize_job_type(value: Any) -> str:
    """Normalize the incoming job type for validation and dispatch."""
    return str(value).strip().lower()


def _normalize_extension(value: Any) -> str:
    """Normalize file extensions by trimming whitespace and leading dots."""
    return str(value).strip().lower().lstrip(".")


def validate_input(job_input: Mapping[str, Any]) -> str | None:
    """Validate the Runpod job payload and return an error message if invalid."""
    job_type = _normalize_job_type(job_input.get("type"))
    if not job_type:
        return "Missing required field: type (video, image, md5, filmstrip)"

    if job_type not in SUPPORTED_JOB_TYPES:
        return (
            f"Invalid type: {job_type}. Must be one of: "
            f"{', '.join(SUPPORTED_JOB_TYPES)}"
        )

    dream_uuid = job_input.get("dream_uuid")
    if not isinstance(dream_uuid, str) or not _is_valid_uuid(dream_uuid):
        return "Missing or invalid dream_uuid (must be a valid UUID)"

    if job_type not in {"video", "image"}:
        return None

    extension = _normalize_extension(job_input.get("extension"))
    if not extension:
        return f"Missing required field: extension for type '{job_type}'"

    allowed_extensions = (
        ALLOWED_VIDEO_TYPES if job_type == "video" else ALLOWED_IMAGE_TYPES
    )
    if extension not in allowed_extensions:
        return (
            f"Invalid {job_type} extension: {extension}. "
            f"Allowed: {sorted(allowed_extensions)}"
        )

    return None


def _build_job_payload(job_input: Mapping[str, Any]) -> dict[str, str]:
    """Build the normalized payload passed to the concrete job runner."""
    payload = {
        "dream_uuid": str(job_input["dream_uuid"]).strip(),
    }

    job_type = _normalize_job_type(job_input["type"])
    if job_type in {"video", "image"}:
        payload["extension"] = _normalize_extension(job_input["extension"])

    return payload


def handler(event: Mapping[str, Any]) -> dict[str, str]:
    """Handle a Runpod event for video-related processing jobs."""
    raw_job_input = event.get("input", {})
    if not isinstance(raw_job_input, Mapping):
        return {"error": "Invalid input payload: input must be an object"}

    error = validate_input(raw_job_input)
    if error:
        return {"error": error}

    job_type = _normalize_job_type(raw_job_input["type"])
    dream_uuid = str(raw_job_input["dream_uuid"]).strip()
    payload = _build_job_payload(raw_job_input)

    print(f"Processing {job_type} job for dream: {dream_uuid}")

    try:
        JOB_RUNNERS[job_type](payload)
    except Exception as exc:
        error_message = str(exc)
        print(f"Job failed for dream {dream_uuid}: {error_message}")
        return {"error": error_message, "type": job_type, "dream_uuid": dream_uuid}

    return {"status": "success", "type": job_type, "dream_uuid": dream_uuid}


runpod.serverless.start({"handler": handler})
