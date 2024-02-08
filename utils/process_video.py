import os
from s3 import download_file, upload_file
from utils.convert_video import convert_video, generate_thumbnail
from api.dream_api import set_dream_processing, set_dream_processed, set_dream_failed

processed_video_suffix = "processed"


def create_process_directory(dream_uuid):
    os.mkdir("./assets/{}".format(dream_uuid))


def remove_generated_files(dream_uuid, extension):
    global processed_video_suffix
    os.remove("./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension))
    os.remove(
        "./assets/{}/{}_{}.mp4".format(dream_uuid, dream_uuid, processed_video_suffix)
    )
    os.remove("./assets/{}/{}.png".format(dream_uuid, dream_uuid))
    os.removedirs("./assets/{}/".format(dream_uuid))


def process_video(user_uuid, dream_uuid, extension):
    download_file(
        file_name="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        object_name="{}/{}/{}.{}".format(user_uuid, dream_uuid, dream_uuid, extension),
    )
    convert_video(
        input_file="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        output_file="./assets/{}/{}_{}.mp4".format(
            dream_uuid, dream_uuid, processed_video_suffix
        ),
    )
    generate_thumbnail(
        input_file="./assets/{}/{}.{}".format(dream_uuid, dream_uuid, extension),
        output_file="./assets/{}/{}.png".format(dream_uuid, dream_uuid),
    )
    # upload video
    upload_file(
        file_name="./assets/{}/{}_{}.mp4".format(
            dream_uuid, dream_uuid, processed_video_suffix
        ),
        object_name="{}/{}/{}_{}.mp4".format(
            user_uuid, dream_uuid, dream_uuid, processed_video_suffix
        ),
    )
    # upload thumbnail
    upload_file(
        file_name="./assets/{}/{}.png".format(dream_uuid, dream_uuid),
        object_name="{}/{}/thumbnails/{}.png".format(user_uuid, dream_uuid, dream_uuid),
    )


def run_process_video(data):
    user_uuid = data["user_uuid"]
    dream_uuid = data["dream_uuid"]
    extension = data["extension"]
    set_dream_processing(dream_uuid)
    create_process_directory(dream_uuid)
    try:
        process_video(user_uuid, dream_uuid, extension)
    except Exception as e:
        print(e)
        remove_generated_files(dream_uuid, extension)
        set_dream_failed(dream_uuid)
        return
    remove_generated_files(dream_uuid, extension)
    set_dream_processed(dream_uuid)
