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
    processed_video_suffix,
    get_file_size,
    create_process_directory,
    remove_process_directory,
)
from clients.edream import edream_client
from edream_sdk.types.dream_types import DreamFileType


def process_video(dream_uuid, extension):
    """
    Executes process video
    """

    dream = edream_client.get_dream(uuid=dream_uuid)
    dream_url = dream["original_video"]
    input_file_path = f"./assets/{dream_uuid}/{dream_uuid}.{extension}"
    
    print(f"Downloading video from: {dream_url}")
    print(f"Download destination: {input_file_path}")
    
    # Check if directory exists before download
    directory_path = os.path.dirname(input_file_path)
    print(f"Directory path: {directory_path}")
    print(f"Directory exists: {os.path.exists(directory_path)}")
    if os.path.exists(directory_path):
        print(f"Directory contents before download: {os.listdir(directory_path)}")
    
    try:
        edream_client.download_file(
            url=dream_url,
            file_path=input_file_path,
        )
        print(f"Download completed")
    except Exception as e:
        print(f"Download failed: {e}")
        raise e
    
    # Check directory contents after download
    if os.path.exists(directory_path):
        print(f"Directory contents after download: {os.listdir(directory_path)}")
    else:
        print(f"Directory does not exist after download: {directory_path}")
    
    # Verify the file was actually downloaded
    if not os.path.exists(input_file_path):
        # List the full assets directory to see what's there
        assets_dir = "./assets"
        if os.path.exists(assets_dir):
            print(f"Assets directory contents: {os.listdir(assets_dir)}")
            # List the specific UUID directory if it exists
            uuid_dir = f"./assets/{dream_uuid}"
            if os.path.exists(uuid_dir):
                print(f"UUID directory contents: {os.listdir(uuid_dir)}")
        raise Exception(f"Downloaded file does not exist: {input_file_path}")
    
    file_size = os.path.getsize(input_file_path)
    print(f"Downloaded file size: {file_size} bytes")

    # Runs video ingestion
    md5 = convert_video(
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
        options={"uuid": dream_uuid, "processed": True},
    )

    # upload thumbnail file
    edream_client.upload_file(
        file_path=f"./assets/{dream_uuid}/{dream_uuid}.png",
        type=DreamFileType.THUMBNAIL,
        options={"uuid": dream_uuid},
    )

    return md5


def process_filmstrip(dream_uuid, video_path, filmstrip_frames_array):
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
            options={"uuid": dream_uuid, "frame_number": frame_number},
        )


def run_video_ingestion(data):
    """
    Runs video ingestion process
    """
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        md5 = process_video(dream_uuid, extension)
        if md5 is None:
            raise Exception("Video processing failed - no MD5 returned")
    except Exception as e:
        print(f"Video processing failed: {e}")
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

    process_filmstrip(dream_uuid, processed_video_path, filmstrip_frames_array)

    edream_client.set_dream_processed(
        uuid=dream_uuid,
        data={
            "processedVideoSize": processed_video_size,
            "processedVideoFrames": processed_video_frames,
            "processedVideoFPS": process_video_fps,
            "activityLevel": 30 / process_video_fps,
            "filmstrip": filmstrip_frames_array,
            "md5": md5,
        },
    )

    remove_process_directory(dream_uuid)
