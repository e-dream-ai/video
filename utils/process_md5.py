import os
from dotenv import load_dotenv
import os
import subprocess
from .file_utils import (
    create_process_directory,
    remove_process_directory,
)

# from api.dream_api import set_dream_processing, set_dream_processed, set_dream_failed
from edream_sdk.client import create_edream_client
from edream_sdk.models.dream_types import SetDreamProcessedRequest, DreamFileType
from edream_sdk.models.file_upload_types import UploadFileOptions

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

# edream sdk client
edream_client = create_edream_client(backend_url=BACKEND_URL, api_key=BACKEND_API_KEY)

processed_video_suffix = "processed"


def process_video_md5(dream_uuid):
    """
    Executes video md5 process
    """

    dream = edream_client.get_dream(uuid=dream_uuid)
    # processed video url
    dream_url = dream.video
    extension = ".mp4"
    video_path = f"./assets/{dream_uuid}/{dream_uuid}_{processed_video_suffix}.mp4"

    edream_client.download_file(
        url=dream_url,
        file_path=f"./assets/{dream_uuid}/{dream_uuid}.{extension}",
    )

    # Runs video ingestion
    md5 = None

    try:
        md5_cmd = ["md5sum", video_path]
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
        print(f"Error: md5sum returned a non-zero exit code ({e.returncode})")

    return md5


def run_video_md5(data):
    """
    Runs video md5 process
    """
    dream_uuid = data["dream_uuid"]

    edream_client.set_dream_processing(uuid=dream_uuid)
    create_process_directory(dream_uuid=dream_uuid)

    try:
        md5 = process_video_md5(dream_uuid)
    except Exception as e:
        print(e)
        remove_process_directory(dream_uuid)
        edream_client.set_dream_failed(uuid=dream_uuid)
        return

    edream_client.set_dream_processed(
        uuid=dream_uuid,
        request_data=SetDreamProcessedRequest(
            md5=md5,
        ),
    )

    remove_process_directory(dream_uuid)
