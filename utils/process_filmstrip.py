import subprocess
from .file_utils import (
    processed_video_suffix,
    get_file_extension,
    create_process_directory,
    remove_process_directory,
)
from .ffmpeg_utils import (
    get_frame_count,
    get_filmstrip_array,
)
from .process_video import process_filmstrip
from clients.edream import edream_client


def process_video_filmstrip(dream_uuid):
    """
    Executes video filmstrip process
    """

    dream = edream_client.get_dream(uuid=dream_uuid)
    # processed video url
    dream_url = dream["video"]
    extension = get_file_extension(dream_url)
    video_path = (
        f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.{extension}"
    )

    edream_client.download_file(
        url=dream_url,
        file_path=video_path,
    )

    filmstrip_frames_array = None

    try:
        processed_video_frames = get_frame_count(video_path)
        filmstrip_frames_array = get_filmstrip_array(
            total_frames=processed_video_frames
        )

        process_filmstrip(dream_uuid, video_path, filmstrip_frames_array)

        return filmstrip_frames_array
    except subprocess.CalledProcessError as e:
        print(
            f"Error: filmstrip generation returned a non-zero exit code ({e.returncode})"
        )

    return filmstrip_frames_array


def run_video_filmstrip(data):
    """
    Runs video filmstrip process
    """
    dream_uuid = data["dream_uuid"]
    create_process_directory(dream_uuid=dream_uuid)

    try:
        filmstrip = process_video_filmstrip(dream_uuid)
    except Exception as e:
        error_message = str(e)
        print(f"Filmstrip processing failed: {error_message}")
        remove_process_directory(dream_uuid)
        edream_client.set_dream_failed(uuid=dream_uuid, error=error_message)
        return

    # set dream processed and save filmstrip
    edream_client.set_dream_processed(
        uuid=dream_uuid,
        data={"filmstrip": filmstrip},
    )

    remove_process_directory(dream_uuid)
