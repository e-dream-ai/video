import hashlib

from clients.edream import edream_client

from .file_utils import (
    create_process_directory,
    get_file_extension,
    processed_video_suffix,
    remove_process_directory,
)


def process_video_md5(dream_uuid: str) -> str:
    """Download the processed video and return its MD5 hash."""
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

    hash_md5 = hashlib.md5()
    with open(video_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(8192), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def run_video_md5(data: dict[str, str]) -> None:
    """Run the processed-video MD5 workflow for a dream."""
    dream_uuid = data["dream_uuid"]
    create_process_directory(dream_uuid=dream_uuid)

    try:
        md5 = process_video_md5(dream_uuid)
        edream_client.set_dream_processed(uuid=dream_uuid, data={"md5": md5})
    except Exception as exc:
        error_message = str(exc)
        print(f"MD5 processing failed: {error_message}")
        edream_client.set_dream_failed(uuid=dream_uuid, error=error_message)
        raise
    finally:
        remove_process_directory(dream_uuid)
