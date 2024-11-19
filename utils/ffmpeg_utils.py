import os
import subprocess
import sys
import platform


def get_hardware_acceleration_codec():
    os_name = platform.system()

    if os_name == "Windows":
        return "libx264"  # software encoder for windows
    elif os_name == "Darwin":
        return "h264_videotoolbox"  # VideoToolbox for macOS
    elif os_name == "Linux":
        return "h264_vaapi"  # VA-API for Linux
    else:
        print(f"Unsupported operating system: {os_name}")
        sys.exit(1)


def convert_video(input_file: str, output_file: str) -> str | None:
    """
    Executes video ingestion
    """
    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-an",
        "-s",
        "1920x1080",
        "-c:v",
        "libx265",
        "-crf",
        "24",
        "-pix_fmt",
        "yuv420p",
        "-tag:v",
        "hvc1",
        "-fps_mode",
        "passthrough",
        "-y",
        output_file,
    ]

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        process.communicate()
        print(f"Success: {input_file} converted to {output_file}")

        md5_cmd = ["md5sum", output_file]
        md5_process = subprocess.Popen(
            md5_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Get output and errors
        stdout, stderr = md5_process.communicate()

        if md5_process.returncode != 0:
            raise Exception(f"Md5 error: {stderr}")

        # extract MD5 from output
        md5 = stdout.split()[0]

        return md5
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg returned a non-zero exit code ({e.returncode})")


def generate_thumbnail(input_file: str, output_file: str):
    cmd = ["ffmpeg", "-i", input_file, "-vframes", "1", "-y", output_file]

    try:
        subprocess.call(cmd)
        print(f"Success: {input_file} extracted {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg returned a non-zero exit code ({e.returncode})")


def get_frame_count(video_path: str):
    """
    Gets video total frames
    """

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


def get_video_fps(video_path: str):
    """
    Gets video frames per second
    """

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


def generate_filmstrip(input_file: str, output_dir: str, filmstrip_frames_array):
    """
    Generates video filmstrip
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # filter string for selecting frames to capture having 1-based frames
    select_frames = "+".join(
        [f"eq(n\\,{frame - 1})" for frame in filmstrip_frames_array]
    )
    temp_output_pattern = os.path.join(output_dir, "temp_frame-%d.jpg")

    # ffmpeg command
    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-vf",
        f"select='{select_frames}',setpts=N/FRAME_RATE/TB",
        "-vsync",
        "vfr",
        temp_output_pattern,
    ]

    try:
        subprocess.call(cmd)
        # rename the frames to match the frame numbers having 1-based
        # ffmpeg output will be 1 to n, regardless of the frames specified
        # so need to be renamed for file output with correct 1-based frame name
        for i, frame_number in enumerate(filmstrip_frames_array, start=1):
            temp_frame_file = os.path.join(output_dir, f"temp_frame-{i}.jpg")
            final_frame_file = os.path.join(output_dir, f"frame-{frame_number}.jpg")
            if os.path.exists(temp_frame_file):
                os.rename(temp_frame_file, final_frame_file)

        print("Success: filmstrip extracted")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg returned a non-zero exit code ({e.returncode})")


def get_filmstrip_array(total_frames: int) -> list[int]:
    if total_frames < 2400:
        frame_step = 100
    else:
        frame_step = 300

    return list(range(1, total_frames + 1, frame_step))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
