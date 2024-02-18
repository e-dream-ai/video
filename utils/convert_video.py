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
        "-s",
        "1920x1080",
        "-c:v",
        "libx264",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-fps_mode",
        "passthrough",
        "-y",
        output_file,
    ]

    try:
        subprocess.call(cmd)
        print("Success: {} converted to {}".format(input_file, output_file))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))


def generate_thumbnail(input_file, output_file_base):
    output_file_png = output_file_base + ".png"
    cmd = ["ffmpeg", "-i", input_file, "-frames:v", "1", "-update", "1", "-y", output_file_png]
    try:
        subprocess.call(cmd)
        print("Success: {} extracted {}".format(input_file, output_file_png))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))
    output_file_1280_jpg = output_file_base + "_1280.jpg"
    output_file_jpg = output_file_base + ".jpg"
    cmd2 = ["ffmpeg", "-i", input_file, "-vf", "scale=160:90", "-frames:v", "1", "-update", "1" , "-y", output_file_jpg]
    try:
        subprocess.call(cmd2)
        print("Success: {} extracted {}".format(input_file, output_file_jpg))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))
    cmd3 = ["ffmpeg", "-i", input_file, "-vf", "scale=1280:720", "-frames:v", "1", "-update", "1" , "-y", output_file_1280_jpg]
    try:
        subprocess.call(cmd3)
        print("Success: {} extracted {}".format(input_file, output_file_jpg))
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
