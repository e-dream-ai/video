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
    hardware_acceleration_codec = get_hardware_acceleration_codec()

    cmd = [
        'ffmpeg',
        '-y', '-vsync', '0',
        '-i', input_file,
        '-an',
        '-t', '600',
        '-c:v', hardware_acceleration_codec,
        '-b:v', '5M',
        output_file
    ]

    try:
        subprocess.call(cmd)
        print('Success: {} converted to {}'.format(input_file, output_file))
    except subprocess.CalledProcessError as e:
        print('Error: FFmpeg returned a non-zero exit code ({})'.format(e.returncode))
        sys.exit(1)

    output_file_png = Path(output_file).stem + '.png'
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vframes', '1',
        output_file_png
    ]

    try:
        subprocess.call(cmd)
        print('Success: {} extracted {}'.format(input_file, output_file_png))
    except subprocess.CalledProcessError as e:
        print('Error: FFmpeg returned a non-zero exit code ({})'.format(e.returncode))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
