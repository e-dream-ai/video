import os
import subprocess
from s3 import download_file, upload_file
from utils.convert_video import convert_video, generate_thumbnail
from api.dream_api import set_dream_processing, set_dream_processed, set_dream_failed

processed_video_suffix = "processed"


def create_process_directory(dream_uuid):
    directory_path = "./assets/{}".format(dream_uuid)
    directory_exists = os.path.exists(directory_path)
    if not directory_exists:
        os.mkdir(directory_path)


def remove_generated_files(dream_uuid):
    directory_path = "./assets/{}/".format(dream_uuid)

    files = os.listdir(directory_path)

    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    if os.path.exists(directory_path):
        os.removedirs(directory_path)


def get_file_size(file_path):
    try:
        # Get the size of the file in bytes
        size_bytes = os.path.getsize(file_path)
        return size_bytes
    except FileNotFoundError:
        return None


def get_frame_count(video_path):
    # Validate if the video path exists
    if not os.path.exists(video_path):
        print("Error: Video path does not exist.")
        return None

    # Run ffprobe command to get total frames
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_frames",
        "-of",
        "default=nokey=1:noprint_wrappers=1",
        video_path,
    ]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    # Capture stdout output
    output, _ = process.communicate()

    # Check if output contains the total number of frames
    if output.strip().isdigit():
        return int(output.strip())
    else:
        print("Error: Unable to get total frames from video.")
        return None


def get_video_fps(video_path):
    # Validate if the video path exists
    if not os.path.exists(video_path):
        print("Error: Video path does not exist.")
        return None

    # Run ffprobe command to get FPS
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    # Capture stdout output
    output, _ = process.communicate()

    # Check if output contains the frame rate
    if "/" in output:
        num, denom = output.strip().split("/")
        if denom != "0":
            return float(num) / float(denom)
        else:
            print("Error: Denominator of FPS is 0.")
            return None
    else:
        print("Error: Unable to get FPS from video.")
        return None


def process_video(user_uuid, dream_uuid, extension):
    download_file(
        file_name="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        object_name="{}/{}/{}.{}".format(user_uuid, dream_uuid, dream_uuid, extension),
    )
    convert_video(
        input_file="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        output_file="./assets/{}/{}_{}.mp4".format(
            dream_uuid, dream_uuid, processed_video_suffix
        ),
    )
    generate_thumbnail(
        input_file="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        output_file="./assets/{}/{}.png".format(dream_uuid, dream_uuid),
    )
    # upload video
    upload_file(
        file_name="./assets/{}/{}_{}.mp4".format(
            dream_uuid, dream_uuid, processed_video_suffix
        ),
        object_name="{}/{}/{}_{}.mp4".format(
            user_uuid, dream_uuid, dream_uuid, processed_video_suffix
        ),
    )
    # upload thumbnail
    upload_file(
        file_name="./assets/{}/{}.png".format(dream_uuid, dream_uuid),
        object_name="{}/{}/thumbnails/{}.png".format(user_uuid, dream_uuid, dream_uuid),
    )


def run_process_video(data):
    user_uuid = data["user_uuid"]
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]
    set_dream_processing(dream_uuid)
    create_process_directory(dream_uuid)
    try:
        process_video(user_uuid, dream_uuid, extension)
    except Exception as e:
        print(e)
        remove_generated_files(dream_uuid)
        set_dream_failed(dream_uuid)
        return
    processed_video_path = "./assets/{}/{}_{}.mp4".format(
        dream_uuid, dream_uuid, processed_video_suffix
    )
    processed_video_size = get_file_size(processed_video_path)
    processed_video_frames = get_frame_count(processed_video_path)
    process_video_fps = get_video_fps(processed_video_path)
    set_dream_processed(
        uuid=dream_uuid,
        processed_video_size=processed_video_size,
        processed_video_frames=processed_video_frames,
        process_video_fps=process_video_fps,
        activity_level=30/process_video_fps,
    )
    remove_generated_files(dream_uuid)
