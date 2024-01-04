import os
import ffmpeg
from flask import Flask
from dotenv import load_dotenv
from flask import jsonify

load_dotenv()

app = Flask(__name__)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


@app.route("/")
def index():
    ffmpeg.input("dummy.mp4").hflip().filter("fps", fps=25, round="up").output(
        "dummy2.mp4"
    ).run(overwrite_output=True)
    return jsonify(sucess=True, status=200, message="Hello world!")
