from dotenv import load_dotenv
load_dotenv()
import os

ENV = os.environ.get('ENV')

if ENV != 'local':
    import bugsnag
    bugsnag.configure(
        api_key="0e46974776f7e4f9ecd2114695d9f3d3",
        project_root="/",
    )
    from bugsnag.flask import handle_exceptions

from flask import Flask, request, jsonify
from rq import Queue
from worker import conn
from utils.process_video import run_process_video


# set default timeout value, 24 hrs
Queue.DEFAULT_TIMEOUT = 60 * 60 * 24

app = Flask(__name__)
if ENV != 'local':
    handle_exceptions(app)
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
