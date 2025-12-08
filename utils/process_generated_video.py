import os
from .ffmpeg_utils import (
    get_frame_count,
    get_video_fps,
    generate_filmstrip,
    get_filmstrip_array,
)
from .file_utils import (
    processed_video_suffix,
    get_file_size,
    create_process_directory,
    remove_process_directory,
)
from clients.edream import edream_client
from edream_sdk.types.dream_types import DreamFileType


def process_generated_video(dream_uuid, video_url):
    dream = edream_client.get_dream(uuid=dream_uuid)
    
    if not video_url.startswith(('http://', 'https://')):
        video_url = f"https://{video_url}"
    
    video_file_path = f"./assets/{dream_uuid}/generated_video.mp4"
    
    print(f"Downloading generated video from: {video_url}")
    
    try:
        result = edream_client.download_file(
            url=video_url,
            file_path=video_file_path,
        )
        
        if result is False:
            raise Exception(f"Download failed - edream_client.download_file returned False")
        
        if not os.path.exists(video_file_path):
            raise Exception(f"Downloaded file does not exist: {video_file_path}")
        
        file_size = os.path.getsize(video_file_path)
        print(f"Download completed - {file_size} bytes")
        
    except Exception as e:
        print(f"Download failed: {e}")
        raise e

    edream_client.upload_file(
        file_path=video_file_path,
        type=DreamFileType.DREAM,
        options={"uuid": dream_uuid, "processed": True},
    )

    return video_file_path


def process_filmstrip(dream_uuid, video_path, filmstrip_frames_array):
    generate_filmstrip(
        input_file=video_path,
        filmstrip_frames_array=filmstrip_frames_array,
        output_dir=f"./assets/{dream_uuid}/filmstrip",
    )

    for frame_number in filmstrip_frames_array:
        edream_client.upload_file(
            file_path=f"./assets/{dream_uuid}/filmstrip/frame-{frame_number}.jpg",
            type=DreamFileType.FILMSTRIP,
            options={"uuid": dream_uuid, "frame_number": frame_number},
        )


def run_process_generated_video(data):
    dream_uuid = data["dream_uuid"]
    video_url = data["video_url"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        video_path = process_generated_video(dream_uuid, video_url)
    except Exception as e:
        print(f"Generated video processing failed: {e}")
        remove_process_directory(dream_uuid)
        edream_client.set_dream_failed(uuid=dream_uuid)
        return

    processed_video_size = get_file_size(video_path)
    processed_video_frames = get_frame_count(video_path)
    process_video_fps = get_video_fps(video_path)
    filmstrip_frames_array = get_filmstrip_array(total_frames=processed_video_frames)

    process_filmstrip(dream_uuid, video_path, filmstrip_frames_array)

    edream_client.set_dream_processed(
        uuid=dream_uuid,
        data={
            "processedVideoSize": processed_video_size,
            "processedVideoFrames": processed_video_frames,
            "processedVideoFPS": process_video_fps,
            "activityLevel": 30 / process_video_fps,
            "filmstrip": filmstrip_frames_array,
        },
    )

    remove_process_directory(dream_uuid)

