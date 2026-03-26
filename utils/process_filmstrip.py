from clients.edream import edream_client

from .ffmpeg_utils import (
    get_filmstrip_array,
    get_frame_count,
)
from .file_utils import (
    create_process_directory,
    get_file_extension,
    processed_video_suffix,
    remove_process_directory,
)
from .process_video import process_filmstrip


def process_video_filmstrip(dream_uuid: str) -> list[int]:
    """Download the processed video and generate its filmstrip frames."""
    dream = edream_client.get_dream(uuid=dream_uuid)
    dream_url = dream["video"]
    extension = get_file_extension(dream_url)
    video_path = (
        f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.{extension}"
    )

    edream_client.download_file(
        url=dream_url,
        file_path=video_path,
    )

    processed_video_frames = get_frame_count(video_path)
    if processed_video_frames is None:
        raise Exception("Filmstrip processing failed - unable to determine frame count")

    filmstrip_frames_array = get_filmstrip_array(
        total_frames=processed_video_frames
    )

    process_filmstrip(dream_uuid, video_path, filmstrip_frames_array)

    return filmstrip_frames_array


def run_video_filmstrip(data: dict[str, str]) -> None:
    """Run the processed-video filmstrip workflow for a dream."""
    dream_uuid = data["dream_uuid"]
    create_process_directory(dream_uuid=dream_uuid)

    try:
        filmstrip = process_video_filmstrip(dream_uuid)
        edream_client.set_dream_processed(
            uuid=dream_uuid,
            data={"filmstrip": filmstrip},
        )
    except Exception as exc:
        error_message = str(exc)
        print(f"Filmstrip processing failed: {error_message}")
        edream_client.set_dream_failed(uuid=dream_uuid, error=error_message)
        raise
    finally:
        remove_process_directory(dream_uuid)
