import os
import subprocess

from PIL import Image

from clients.edream import edream_client
from edream_sdk.types.dream_types import DreamFileType, DreamMediaType

from .file_utils import (
    create_process_directory,
    get_file_size,
    processed_video_suffix,
    remove_process_directory,
)


def convert_image_to_webp(input_file: str, output_file: str) -> str:
    """Convert an image to WebP with quality-oriented ImageMagick settings."""
    try:
        subprocess.run(
            [
                "convert",
                input_file,
                "-quality",
                "90",
                "-define",
                "webp:method=6",
                output_file,
            ],
            check=True,
            capture_output=True,
        )

        if not os.path.exists(output_file):
            raise Exception(
                "ImageMagick conversion failed - output file not created: "
                f"{output_file}"
            )

        return output_file
    except subprocess.CalledProcessError as e:
        raise Exception(f"ImageMagick conversion failed: {e.stderr.decode()}")
    except FileNotFoundError:
        raise Exception(
            "ImageMagick 'convert' command not found. Please install ImageMagick."
        )


def get_image_resolution(image_path: str) -> tuple[int, int] | None:
    """Return image resolution as `(width, height)` in pixels."""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        print(f"Failed to get image resolution: {e}")
        return None


def calculate_md5(file_path: str) -> str:
    """Calculate the MD5 hash for a file."""
    import hashlib

    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def process_image(dream_uuid: str, extension: str) -> dict:
    """Download, convert, upload, and summarize an image processing job."""
    dream = edream_client.get_dream(uuid=dream_uuid)
    dream_url = dream["original_video"]

    if not dream_url.startswith(("http://", "https://")):
        dream_url = f"https://{dream_url}"

    input_file_path = f"./assets/{dream_uuid}/{dream_uuid}.{extension}"
    output_file_path = (
        f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.webp"
    )

    print(f"Downloading image from: {dream_url}")

    try:
        result = edream_client.download_file(
            url=dream_url,
            file_path=input_file_path,
        )

        if result is False:
            raise Exception(
                f"Download failed - edream_client.download_file returned False"
            )

        if not os.path.exists(input_file_path):
            raise Exception(f"Downloaded file does not exist: {input_file_path}")

        file_size = os.path.getsize(input_file_path)
        print(f"Download completed - {file_size} bytes")

    except Exception as exc:
        print(f"Download failed: {exc}")
        raise

    image_resolution = get_image_resolution(input_file_path)
    processed_media_width = None
    processed_media_height = None

    if image_resolution is not None:
        processed_media_width, processed_media_height = image_resolution

    print(f"Converting image to WebP: {input_file_path} -> {output_file_path}")
    convert_image_to_webp(input_file_path, output_file_path)

    md5 = calculate_md5(output_file_path)

    edream_client.upload_file(
        file_path=output_file_path,
        type=DreamFileType.DREAM,
        options={"uuid": dream_uuid, "processed": True},
    )

    edream_client.upload_file(
        file_path=output_file_path,
        type=DreamFileType.THUMBNAIL,
        options={"uuid": dream_uuid},
    )

    processed_file_size = get_file_size(output_file_path)

    return {
        "processedMediaWidth": processed_media_width,
        "processedMediaHeight": processed_media_height,
        "processedVideoSize": processed_file_size,
        "md5": md5,
    }


def run_image_ingestion(data: dict[str, str]) -> None:
    """Run the image ingestion workflow for a dream."""
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        metadata = process_image(dream_uuid, extension)
        if metadata is None:
            raise Exception("Image processing failed - no metadata returned")
        edream_client.set_dream_processed(
            uuid=dream_uuid,
            data={
                "processedVideoSize": metadata["processedVideoSize"],
                "processedMediaWidth": metadata["processedMediaWidth"],
                "processedMediaHeight": metadata["processedMediaHeight"],
                "md5": metadata["md5"],
                "mediaType": DreamMediaType.IMAGE,
                "filmstrip": None,
            },
        )
    except Exception as exc:
        error_message = str(exc)
        print(f"Image processing failed: {error_message}")
        edream_client.set_dream_failed(uuid=dream_uuid, error=error_message)
        raise
    finally:
        remove_process_directory(dream_uuid)
