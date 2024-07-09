import os
import redis
import logging
from rq import Worker, Queue, Connection
from rq.registry import FailedJobRegistry
from config import Env

env = os.getenv("ENV")
listen = ["high", "default", "low"]
redis_url = os.getenv("REDISCLOUD_URL", "redis://localhost:6379")
conn = redis.from_url(redis_url)

# # Configure RQ worker logging
if env == Env.LOCAL:
    logging.basicConfig(
        level=logging.DEBUG,  # Match the logging level with the main app
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("rq_worker.log"), logging.StreamHandler()],
    )
else:
    logging.basicConfig(
        level=logging.WARNING,  # Set to WARNING to capture warnings and errors
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


# requeue failed jobs function
def requeue_failed_jobs():
    with Connection(conn):
        for name in listen:
            queue = Queue(name=name, connection=conn)
            registry = FailedJobRegistry(queue=queue)
            # Retrieve IDs of all failed jobs
            failed_job_ids = registry.get_job_ids()
            for job_id in failed_job_ids:
                job = queue.fetch_job(job_id)
                if job:  # If the job exists and has not been removed
                    # Requeue the job
                    result = job.requeue()
                    print(f"Requeued job {job_id} from the {name} queue")
                    if result:
                        # Remove the job from registry
                        registry.remove(job_id, delete_job=False)


if __name__ == "__main__":
    with Connection(conn):
        queues = [Queue(name=name) for name in listen]
        worker = Worker(queues=queues)
        worker.work()
        requeue_failed_jobs()
