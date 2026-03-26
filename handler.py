import runpod
from clients.edream import init_edream

init_edream()

from utils.process_video import run_video_ingestion
from utils.process_md5 import run_video_md5
from utils.process_filmstrip import run_video_filmstrip
from utils.process_image import run_image_ingestion

ALLOWED_VIDEO_TYPES = [
    "mp4", "avi", "mov", "wmv", "mkv", "flv", "mpeg",
    "webm", "ogv", "3gp", "3g2", "h264", "hevc", "divx", "xvid", "avchd",
]
ALLOWED_IMAGE_TYPES = [
    "jpg", "jpeg", "png", "gif", "bmp", "webp",
    "tiff", "svg", "ico", "heif", "heic",
]


def validate_input(job_input):
    job_type = job_input.get("type")
    if not job_type:
        return "Missing required field: type (video, image, md5, filmstrip)"

    dream_uuid = job_input.get("dream_uuid")
    if not dream_uuid or len(dream_uuid) != 36:
        return "Missing or invalid dream_uuid (must be 36 characters)"

    if job_type in ("video", "image"):
        extension = job_input.get("extension")
        if not extension:
            return f"Missing required field: extension for type '{job_type}'"

        if job_type == "video" and extension not in ALLOWED_VIDEO_TYPES:
            return f"Invalid video extension: {extension}. Allowed: {ALLOWED_VIDEO_TYPES}"
        if job_type == "image" and extension not in ALLOWED_IMAGE_TYPES:
            return f"Invalid image extension: {extension}. Allowed: {ALLOWED_IMAGE_TYPES}"

    if job_type not in ("video", "image", "md5", "filmstrip"):
        return f"Invalid type: {job_type}. Must be one of: video, image, md5, filmstrip"

    return None


def handler(event):
    job_input = event.get("input", {})

    # Validate input
    error = validate_input(job_input)
    if error:
        return {"error": error}

    job_type = job_input["type"]
    dream_uuid = job_input["dream_uuid"]

    print(f"Processing {job_type} job for dream: {dream_uuid}")

    try:
        if job_type == "video":
            data = {"dream_uuid": dream_uuid, "extension": job_input["extension"]}
            run_video_ingestion(data)
            return {"status": "success", "type": "video", "dream_uuid": dream_uuid}

        elif job_type == "image":
            data = {"dream_uuid": dream_uuid, "extension": job_input["extension"]}
            run_image_ingestion(data)
            return {"status": "success", "type": "image", "dream_uuid": dream_uuid}

        elif job_type == "md5":
            data = {"dream_uuid": dream_uuid}
            run_video_md5(data)
            return {"status": "success", "type": "md5", "dream_uuid": dream_uuid}

        elif job_type == "filmstrip":
            data = {"dream_uuid": dream_uuid}
            run_video_filmstrip(data)
            return {"status": "success", "type": "filmstrip", "dream_uuid": dream_uuid}

    except Exception as e:
        error_msg = str(e)
        print(f"Job failed for dream {dream_uuid}: {error_msg}")
        return {"error": error_msg, "type": job_type, "dream_uuid": dream_uuid}


runpod.serverless.start({"handler": handler})
