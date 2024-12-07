import os

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


def get_file_extension(file_name):
    if not file_name:
        return ""
    dot_index = file_name.rfind(".")
    if dot_index != -1:
        return file_name[dot_index + 1 :].lower()
    return ""


def create_process_directory(dream_uuid: str):
    """
    Creates process directory
    """
    directory_path = f"./assets/{dream_uuid}"
    directory_exists = os.path.exists(directory_path)
    if not directory_exists:
        os.mkdir(directory_path)


def remove_process_directory(dream_uuid: str):
    """
    Removes process directory and its files
    """

    # filmstrip directory
    filmstrip_directory_path = f"./assets/{dream_uuid}/filmstrip"

    if os.path.exists(filmstrip_directory_path):
        filmstrip_files = os.listdir(filmstrip_directory_path)

        for file in filmstrip_files:
            file_path = os.path.join(filmstrip_directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        os.removedirs(filmstrip_directory_path)

    # dream directory
    directory_path = f"./assets/{dream_uuid}/"
    files = os.listdir(directory_path)

    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    if os.path.exists(directory_path):
        os.removedirs(directory_path)
