import os
from dotenv import load_dotenv
from .ffmpeg_utils import (
    convert_video,
    generate_thumbnail,
    get_frame_count,
    get_video_fps,
    generate_filmstrip,
    get_filmstrip_array,
)
from .file_utils import (
    get_file_size,
    create_process_directory,
    remove_process_directory,
)

# from api.dream_api import set_dream_processing, set_dream_processed, set_dream_failed
from edream_sdk.client import create_edream_client
from edream_sdk.models.dream_types import SetDreamProcessedRequest, DreamFileType
from edream_sdk.models.file_upload_types import UploadFileOptions

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

# edream sdk client
edream_client = create_edream_client(backend_url=BACKEND_URL, api_key=BACKEND_API_KEY)

processed_video_suffix = "processed"


def process_video(user_uuid, dream_uuid, extension):
    """
    Executes process video
    """

    dream = edream_client.get_dream(uuid=dream_uuid)
    dream_url = dream.original_video

    edream_client.download_file(
        url=dream_url,
        file_path=f"./assets/{dream_uuid}/{dream_uuid}.{extension}",
    )

    # Runs video ingestion
    convert_video(
        input_file=f"./assets/{dream_uuid}/{dream_uuid}.{extension}",
        output_file=f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4",
    )

    # Generate thumbnail
    generate_thumbnail(
        input_file=f"./assets/{dream_uuid}/{dream_uuid}.{extension}",
        output_file=f"./assets/{dream_uuid}/{dream_uuid}.png",
    )

    # Upload MP4 video file
    edream_client.upload_file(
        file_path=f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4",
        type=DreamFileType.DREAM,
        options=UploadFileOptions(uuid=dream_uuid, processed=True),
    )

    # upload thumbnail file
    edream_client.upload_file(
        file_path=f"./assets/{dream_uuid}/{dream_uuid}.png",
        type=DreamFileType.THUMBNAIL,
        options=UploadFileOptions(uuid=dream_uuid),
    )


def process_filmstrip(user_uuid, dream_uuid, video_path, filmstrip_frames_array):
    """
    Executes process filmstrip
    """
    generate_filmstrip(
        input_file=video_path,
        filmstrip_frames_array=filmstrip_frames_array,
        output_dir=f"./assets/{dream_uuid}/filmstrip",
    )

    for frame_number in filmstrip_frames_array:
        edream_client.upload_file(
            file_path=f"./assets/{dream_uuid}/filmstrip/frame-{frame_number}.jpg",
            type=DreamFileType.FILMSTRIP,
            options=UploadFileOptions(uuid=dream_uuid, frame_number=frame_number),
        )


def run_video_ingestion(data):
    """
    Runs video ingestion process
    """
    user_uuid = data["user_uuid"]
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        process_video(user_uuid, dream_uuid, extension)
    except Exception as e:
        print(e)
        remove_process_directory(dream_uuid)
        edream_client.set_dream_failed(uuid=dream_uuid)
        return

    processed_video_path = (
        f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4"
    )
    processed_video_size = get_file_size(processed_video_path)
    processed_video_frames = get_frame_count(processed_video_path)
    process_video_fps = get_video_fps(processed_video_path)
    filmstrip_frames_array = get_filmstrip_array(total_frames=processed_video_frames)

    process_filmstrip(
        user_uuid, dream_uuid, processed_video_path, filmstrip_frames_array
    )

    edream_client.set_dream_processed(
        uuid=dream_uuid,
        request_data=SetDreamProcessedRequest(
            processed_video_size=processed_video_size,
            processed_video_frames=processed_video_frames,
            process_video_fps=process_video_fps,
            activity_level=30 / process_video_fps,
            filmstrip_frames_array=filmstrip_frames_array,
        ),
    )

    remove_process_directory(dream_uuid)
