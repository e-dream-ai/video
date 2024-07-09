import requests
from api.api import get_session, get_backend_url, load_api

load_api()
BACKEND_URL = get_backend_url()


def set_dream_processing(uuid: str):
    session = get_session()
    try:
        session.post(
            "{}/dream/{}/status/processing".format(BACKEND_URL, uuid),
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def set_dream_processed(
    uuid: str,
    processed_video_size: int | None,
    processed_video_frames: int | None,
    process_video_fps: int | None,
    activity_level: float | None,
    filmstrip_frames_array,
):
    session = get_session()
    json_data = {
        "processedVideoSize": processed_video_size,
        "processedVideoFrames": processed_video_frames,
        "processedVideoFPS": process_video_fps,
        "activityLevel": activity_level,
        "filmstrip": filmstrip_frames_array,
    }
    try:
        session.post(
            "{}/dream/{}/status/processed".format(BACKEND_URL, uuid), json=json_data
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])


def set_dream_failed(uuid: str):
    session = get_session()
    try:
        session.post(
            "{}/dream/{}/status/failed".format(BACKEND_URL, uuid),
        )
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
