import os
import ffmpeg
from s3 import download_file, upload_file
from convert_video import convert_video, generate_thumbnail
from flask import Flask
from dotenv import load_dotenv
from flask import jsonify

load_dotenv()

app = Flask(__name__)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


@app.route("/convert_video")
def index():
    dream_uuid = "177d577d-99f8-4125-9584-0656eb6b7f5f"
    user_uuid = "0cfcfb03-cab5-490a-b7cf-3ab8bfd4f51c"
    is_dream_downloaded = download_file(
        file_name="./assets/{}.mp4".format(dream_uuid),
        object_name="{}/{}/{}.mp4".format(user_uuid, dream_uuid, dream_uuid),
    )

    if not is_dream_downloaded:
        return jsonify(sucess=False, status=404, message="Dream not found")
    convert_video(
        input_file="./assets/{}.mp4".format(dream_uuid),
        output_file="./assets/{}_output.mp4".format(dream_uuid),
    )
    generate_thumbnail(
        input_file="./assets/{}.mp4".format(dream_uuid),
        output_file="./assets/{}.png".format(dream_uuid),
    )
    upload_file(
        file_name="./assets/{}.mp4".format(dream_uuid),
        object_name="{}/{}/{}_converted.mp4".format(user_uuid, dream_uuid, dream_uuid),
    )
    upload_file(
        file_name="./assets/{}.png".format(dream_uuid),
        object_name="{}/{}/{}.png".format(user_uuid, dream_uuid, dream_uuid),
    )

    return jsonify(sucess=True, status=200, message="Video successfully converted")
