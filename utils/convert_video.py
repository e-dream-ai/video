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


def generate_filmstrip(input_file, output_dir, filmstrip_frames_array):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # filter string for selecting frames
    select_frames = "+".join([f"eq(n\\,{frame})" for frame in filmstrip_frames_array])
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
        # rename the frames to match the frame numbers
        for i, frame_number in enumerate(filmstrip_frames_array, start=1):
            temp_frame_file = os.path.join(output_dir, f"temp_frame-{i}.jpg")
            final_frame_file = os.path.join(output_dir, f"frame-{frame_number}.jpg")
            if os.path.exists(temp_frame_file):
                os.rename(temp_frame_file, final_frame_file)

        print("Success: filmstrip extracted")
    except subprocess.CalledProcessError as e:
        print("Error: FFmpeg returned a non-zero exit code ({})".format(e.returncode))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
