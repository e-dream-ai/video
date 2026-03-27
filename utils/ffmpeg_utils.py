import os
import subprocess
import sys
import hashlib


def _check_nvenc_available() -> bool:
    """Check if NVIDIA NVENC hardware encoder is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=10
        )
        return "hevc_nvenc" in result.stdout
    except Exception:
        return False


GPU_AVAILABLE = _check_nvenc_available()
print(f"GPU NVENC available: {GPU_AVAILABLE}")


def _calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file using hashlib."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def convert_video(input_file: str, output_file: str) -> str | None:
    """
    Executes video ingestion with GPU acceleration (NVENC) if available,
    falls back to CPU encoding otherwise.
    """
    if GPU_AVAILABLE:
        cmd = [
            "ffmpeg",
            "-hwaccel", "cuda",
            "-hwaccel_output_format", "cuda",
            "-extra_hw_frames", "4",
            "-i", input_file,
            "-an",
            "-vf", "scale_npp=1920:1080:interp_algo=lanczos",
            "-c:v", "hevc_nvenc",
            "-preset", "p5",
            "-rc", "vbr",
            "-cq", "24",
            "-b:v", "0",
            "-tag:v", "hvc1",
            "-fps_mode", "passthrough",
            "-y", output_file,
        ]
        print(f"Starting GPU-accelerated video conversion: {input_file}")
    else:
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-an",
            "-s", "1920x1080",
            "-c:v", "libx265",
            "-crf", "24",
            "-pix_fmt", "yuv420p",
            "-tag:v", "hvc1",
            "-fps_mode", "passthrough",
            "-y", output_file,
        ]
        print(f"Starting CPU video conversion (no GPU detected): {input_file}")

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0 and GPU_AVAILABLE:
            print(f"GPU encoding failed (exit code {process.returncode}), falling back to CPU. Error: {stderr[-1000:] if stderr else 'unknown error'}")
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-an",
                "-s", "1920x1080",
                "-c:v", "libx265",
                "-crf", "24",
                "-pix_fmt", "yuv420p",
                "-tag:v", "hvc1",
                "-fps_mode", "passthrough",
                "-y", output_file,
            ]
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"FFmpeg conversion failed with return code {process.returncode}")
            if stderr:
                print(f"FFmpeg error: {stderr}")
            return None

        if not os.path.exists(output_file):
            print(f"Error: Output file does not exist after conversion")
            return None

        print(f"Video conversion completed successfully")

        md5 = _calculate_md5(output_file)
        print(f"MD5 calculated: {md5}")

        return md5
    except Exception as e:
        print(f"Error during video conversion: {e}")
        return None


def generate_thumbnail(input_file: str, output_file: str):
    """
    Generates an optimized thumbnail from a video file.
    Resizes to 4K maximum, but never upscales if input is smaller.
    Reduces to 8bpp, and applies PNG compression.
    """
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vframes", "1",
        "-vf", "scale='min(iw,3840)':'min(ih,2160)':force_original_aspect_ratio=decrease",
        "-pix_fmt", "rgb24",
        "-compression_level", "6", 
        "-y", output_file
    ]

    try:
        subprocess.call(cmd)
        print(f"Success: {input_file} extracted {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg returned a non-zero exit code ({e.returncode})")


def get_frame_count(video_path: str):
    """
    Gets video total frames
    returns total_frames (int)
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


def get_video_resolution(video_path: str):
    """
    Gets video resolution (width and height in pixels)
    """

    if not os.path.exists(video_path):
        print("Error: Video path does not exist.")
        return None

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
        video_path,
    ]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    output, _ = process.communicate()

    if "x" in output:
        try:
            width_str, height_str = output.strip().split("x")
            width = int(width_str)
            height = int(height_str)
            return width, height
        except ValueError:
            print("Error: Unable to parse video resolution.")
            return None

    print("Error: Unable to get resolution from video.")
    return None


def generate_filmstrip(input_file: str, output_dir: str, filmstrip_frames_array):
    """
    Generates video filmstrip with optimized frame sizes.
    Resizes frames to maximum 1920x1080 to reduce file sizes.
    Uses CUDA hardware acceleration for decoding when available.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # filter string for selecting frames to capture
    select_frames = "+".join([f"eq(n\\,{frame})" for frame in filmstrip_frames_array])
    temp_output_pattern = os.path.join(output_dir, "temp_frame-%d.jpg")

    cmd = ["ffmpeg"]
    if GPU_AVAILABLE:
        cmd += ["-hwaccel", "cuda"]
    cmd += [
        "-i", input_file,
        "-vf",
        f"select='{select_frames}',setpts=N/FRAME_RATE/TB,scale=1920:1080:force_original_aspect_ratio=decrease",
        "-vsync", "vfr",
        "-q:v", "3",
        "-start_number", "0",
        temp_output_pattern,
    ]

    try:
        subprocess.call(cmd)
        # ffmpeg outputs sequentially numbered files (e.g. temp_frame-0.jpg)
        # the renaming process maps these to the actual frame numbers in filmstrip_frames_array (e.g. temp_frame-0.jpg -> frame-10.jpg)
        # ffmpeg output will be 1 to n, regardless of the frames specified
        for i, frame_number in enumerate(filmstrip_frames_array, start=0):
            temp_frame_file = os.path.join(output_dir, f"temp_frame-{i}.jpg")
            final_frame_file = os.path.join(output_dir, f"frame-{frame_number}.jpg")
            # need to be renamed from 1-based ffmpeg frame output to zero-based frame handling
            if os.path.exists(temp_frame_file):
                os.rename(temp_frame_file, final_frame_file)

        print("Success: filmstrip extracted")
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg returned a non-zero exit code ({e.returncode})")


def get_filmstrip_array(total_frames: int) -> list[int]:
    """
    Generates a list of frames to create a filmstrip from a video.
    The frames are selected at regular intervals (every 100 frames for videos with fewer than 2400 frames, or every 300 frames for longer videos).
    Last frame is included.
    Important: frame numbering is zero-based, meaning the first frame is frame 0 and the last frame is frame `total_frames - 1`.
    Example:
        >>> get_filmstrip_array(1200)
        [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1199]  # 1200 frames, last frame is 1199
    """

    # if the dream < 2400 frames total then, every filmstrip every 100 frames, otherwise 300
    if total_frames < 2400:
        frame_step = 100
    else:
        frame_step = 300

    frames = list(range(0, total_frames, frame_step))
    # verifies if last frame is on list
    # since frames are zero-based, last frame should be n - 1
    last_frame = total_frames - 1
    if frames[-1] != last_frame:
        frames.append(last_frame)

    return frames


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_video.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_video(input_file, output_file)
