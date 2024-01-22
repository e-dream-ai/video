import subprocess
import sys
import platform
from pathlib import Path


def get_hardware_acceleration_codec():
    os_name = platform.system()

    if os_name == "Windows":
        return "libx264"  # software encoder for windows
    elif os_name == "Darwin":
        return "h264_videotoolbox"  # VideoToolbox for macOS
    elif os_name == "Linux":
        return "h264_vaapi"  # VA-API for Linux
    else:
        print("Unsupported operating system: {}".format(os_name))
        sys.exit(1)


def convert_video(input_file, output_file):
    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-an",
        "-t",
        "600",
        "-s",
        "1920x1080",
        "-c:v",
        "libx264",
        "-crf",
        "20",
        "-fps_mode",
        "passthrough",
        "-y",
        output_file,
        "-report",
    ]

    try:
        subprocess.call(cmd)
        print("Success: {} converted to {}".format(input_file, output_file))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))


def generate_thumbnail(input_file, output_file):
    cmd = ["ffmpeg", "-i", input_file, "-vframes", "1", "-y", output_file]

    try:
        subprocess.call(cmd)
        print("Success: {} extracted {}".format(input_file, output_file))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
