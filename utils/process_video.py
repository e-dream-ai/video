import os
from concurrent.futures import ThreadPoolExecutor

from clients.edream import edream_client
from edream_sdk.types.dream_types import DreamFileType, DreamMediaType

from .ffmpeg_utils import (
    convert_video,
    generate_filmstrip,
    generate_thumbnail,
    get_filmstrip_array,
    get_frame_count,
    get_video_fps,
    get_video_resolution,
)
from .file_utils import (
    create_process_directory,
    get_file_size,
    processed_video_suffix,
    remove_process_directory,
)


def process_video(dream_uuid: str, extension: str) -> str | None:
    """Download, transcode, thumbnail, and upload the processed video."""
    dream = edream_client.get_dream(uuid=dream_uuid)
    dream_url = dream["original_video"]

    if not dream_url.startswith(("http://", "https://")):
        dream_url = f"https://{dream_url}"

    input_file_path = f"./assets/{dream_uuid}/{dream_uuid}.{extension}"
    print(f"Downloading video from: {dream_url}")

    try:
        result = edream_client.download_file(
            url=dream_url,
            file_path=input_file_path,
        )

        if result is False:
            raise Exception(
                "Download failed - edream_client.download_file returned False"
            )

        if not os.path.exists(input_file_path):
            raise Exception(f"Downloaded file does not exist: {input_file_path}")

        file_size = os.path.getsize(input_file_path)
        print(f"Download completed - {file_size} bytes")
    except Exception as exc:
        print(f"Download failed: {exc}")
        raise

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_convert = executor.submit(
            convert_video,
            input_file=input_file_path,
            output_file=f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4",
        )
        future_thumbnail = executor.submit(
            generate_thumbnail,
            input_file=input_file_path,
            output_file=f"./assets/{dream_uuid}/{dream_uuid}.png",
        )
        md5 = future_convert.result()
        future_thumbnail.result()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_video_upload = executor.submit(
            edream_client.upload_file,
            file_path=f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4",
            type=DreamFileType.DREAM,
            options={"uuid": dream_uuid, "processed": True},
        )
        future_thumbnail_upload = executor.submit(
            edream_client.upload_file,
            file_path=f"./assets/{dream_uuid}/{dream_uuid}.png",
            type=DreamFileType.THUMBNAIL,
            options={"uuid": dream_uuid},
        )
        future_video_upload.result()
        future_thumbnail_upload.result()

    return md5


def process_filmstrip(
    dream_uuid: str,
    video_path: str,
    filmstrip_frames_array: list[int],
) -> None:
    """Generate and upload filmstrip frames for a processed video."""
    generate_filmstrip(
        input_file=video_path,
        filmstrip_frames_array=filmstrip_frames_array,
        output_dir=f"./assets/{dream_uuid}/filmstrip",
    )

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(
                edream_client.upload_file,
                file_path=f"./assets/{dream_uuid}/filmstrip/frame-{frame_number}.jpg",
                type=DreamFileType.FILMSTRIP,
                options={"uuid": dream_uuid, "frame_number": frame_number},
            )
            for frame_number in filmstrip_frames_array
        ]
        for future in futures:
            future.result()


def run_video_ingestion(data: dict[str, str]) -> None:
    """Run the full video ingestion workflow for a dream."""
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        md5 = process_video(dream_uuid, extension)
        if md5 is None:
            raise Exception("Video processing failed - no MD5 returned")
        processed_video_path = (
            f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4"
        )
        original_video_path = f"./assets/{dream_uuid}/{dream_uuid}.{extension}"
        processed_video_size = get_file_size(processed_video_path)
        processed_video_frames = get_frame_count(processed_video_path)
        process_video_fps = get_video_fps(processed_video_path)
        video_resolution = get_video_resolution(original_video_path)
        processed_media_width = None
        processed_media_height = None

        if video_resolution is not None:
            processed_media_width, processed_media_height = video_resolution

        filmstrip_frames_array = get_filmstrip_array(total_frames=processed_video_frames)
        process_filmstrip(dream_uuid, processed_video_path, filmstrip_frames_array)

        edream_client.set_dream_processed(
            uuid=dream_uuid,
            data={
                "processedVideoSize": processed_video_size,
                "processedVideoFrames": processed_video_frames,
                "processedVideoFPS": process_video_fps,
                "processedMediaWidth": processed_media_width,
                "processedMediaHeight": processed_media_height,
                "activityLevel": 30 / process_video_fps,
                "filmstrip": filmstrip_frames_array,
                "md5": md5,
                "mediaType": DreamMediaType.VIDEO,
            },
        )
    except Exception as exc:
        error_message = str(exc)
        print(f"Video processing failed: {error_message}")
        edream_client.set_dream_failed(uuid=dream_uuid, error=error_message)
        raise
    finally:
        remove_process_directory(dream_uuid)
