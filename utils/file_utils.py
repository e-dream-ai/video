import os
import shutil

processed_video_suffix = "processed"


def get_file_size(file_path: str) -> int | None:
    """
    Gets file size in bytes
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes
    except FileNotFoundError:
        return None


def get_file_extension(file_name: str | None) -> str:
    """Return the lowercase extension for a file name or URL."""
    if not file_name:
        return ""
    dot_index = file_name.rfind(".")
    if dot_index != -1:
        return file_name[dot_index + 1 :].lower()
    return ""


def create_process_directory(dream_uuid: str):
    """Create the per-dream processing directory if it does not exist."""
    directory_path = f"./assets/{dream_uuid}"
    directory_exists = os.path.exists(directory_path)
    if not directory_exists:
        os.mkdir(directory_path)


def remove_process_directory(dream_uuid: str):
    """Remove the per-dream processing directory and any generated files."""
    directory_path = f"./assets/{dream_uuid}"
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
