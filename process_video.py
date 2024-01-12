import os
from s3 import download_file, upload_file
from convert_video import convert_video, generate_thumbnail


def process_video(user_uuid, dream_uuid):
    print(f"processing user_uuid: {user_uuid}")
    print(f"processing dream_uuid: {dream_uuid}")
    download_file(
        file_name="./assets/{}.mp4".format(dream_uuid),
        object_name="{}/{}/{}.mp4".format(user_uuid, dream_uuid, dream_uuid),
    )

    convert_video(
        input_file="./assets/{}.mp4".format(dream_uuid),
        output_file="./assets/{}_processed.mp4".format(dream_uuid),
    )
    generate_thumbnail(
        input_file="./assets/{}.mp4".format(dream_uuid),
        output_file="./assets/{}.png".format(dream_uuid),
    )
    upload_file(
        file_name="./assets/{}.mp4".format(dream_uuid),
        object_name="{}/{}/{}_processed.mp4".format(user_uuid, dream_uuid, dream_uuid),
    )
    upload_file(
        file_name="./assets/{}.png".format(dream_uuid),
        object_name="{}/{}/thumbnails/{}.png".format(user_uuid, dream_uuid, dream_uuid),
    )

    os.remove("./assets/{}.mp4".format(dream_uuid))
    os.remove("./assets/{}_processed.mp4".format(dream_uuid))
    os.remove("./assets/{}.png".format(dream_uuid))
