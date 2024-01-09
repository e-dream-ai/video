import os
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from process_video import process_video


load_dotenv()

app = Flask(__name__)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


@app.route("/process_video", methods=["POST"])
def process_video_handler():
    content = request.json
    user_uuid = content["user_uuid"]
    dream_uuid = content["dream_uuid"]

    thread = threading.Thread(target=process_video, args=(user_uuid, dream_uuid))
    thread.start()

    return jsonify(sucess=True, status=200, message="Video successfully converted")
