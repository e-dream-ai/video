import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from rq import Queue
from worker import conn
from utils.process_video import run_process_video

load_dotenv()

# set default timeout value
Queue.DEFAULT_TIMEOUT = 3600

app = Flask(__name__)
q = Queue(connection=conn)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


def get_job_status(job):
    status = {
        "id": job.id,
        "result": job.result,
        "status": "failed"
        if job.is_failed
        else "pending"
        if job.result == None
        else "completed",
    }
    status.update(job.meta)
    return status


@app.route("/process-video", methods=["POST"])
def process_video_handler():
    data = request.json
    new_job = q.enqueue(run_process_video, args=(data,))
    output = get_job_status(new_job)
    return jsonify(output)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
