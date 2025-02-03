import os
import logging
from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
from rq import Queue
from worker import conn
from utils.process_video import run_video_ingestion
from utils.process_md5 import run_video_md5
from utils.process_filmstrip import run_video_filmstrip
from decorators.api_key_decorator import api_key_required
from config import Env
from marshmallow import ValidationError
from schemas.process_video_schema import VideoProcessSchema, VideoMd5Schema, VideoFilmstripSchema

load_dotenv()

# set default timeout value, 24 hrs
Queue.DEFAULT_TIMEOUT = 60 * 60 * 24

app = Flask(__name__)
q = Queue(connection=conn)
env = os.getenv("ENV")
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


# Configure flask logging
if env == Env.LOCAL:
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to capture all logs
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("flask.log"), logging.StreamHandler()],
    )
else:
    logging.basicConfig(
        level=logging.WARNING,  # Set to WARNING to capture warnings and errors
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def get_job_status(job):
    status = {
        "id": job.id,
        "result": job.result,
        "status": (
            "failed"
            if job.is_failed
            else "pending" if job.result == None else "completed"
        ),
    }
    status.update(job.meta)
    return status


@app.route("/process-video", methods=["POST"])
@api_key_required
def process_video_handler():
    data = request.json
    schema = VideoProcessSchema()
    try:
        validated_data = schema.load(data)
        new_job = q.enqueue(run_video_ingestion, args=(validated_data,))
        output = get_job_status(new_job)
        return jsonify(output)
    except ValidationError as err:
        return make_response(jsonify({"sucess": False, "message": err.messages}), 400)


@app.route("/video/md5", methods=["POST"])
@api_key_required
def process_video_md5_handler():
    data = request.json
    schema = VideoMd5Schema()
    try:
        validated_data = schema.load(data)
        new_job = q.enqueue(run_video_md5, args=(validated_data,))
        output = get_job_status(new_job)
        return jsonify(output)
    except ValidationError as err:
        return make_response(jsonify({"sucess": False, "message": err.messages}), 400)


@app.route("/video/filmstrip", methods=["POST"])
@api_key_required
def process_video_filmstrip_handler():
    data = request.json
    schema = VideoFilmstripSchema()
    try:
        validated_data = schema.load(data)
        new_job = q.enqueue(run_video_filmstrip, args=(validated_data,))
        output = get_job_status(new_job)
        return jsonify(output)
    except ValidationError as err:
        return make_response(jsonify({"sucess": False, "message": err.messages}), 400)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
