import os
import redis
from rq import Worker, Queue, Connection

DEFAULT_QUEUE_TIMEOUT = 3600

listen = ["high", "default", "low"]

redis_url = os.getenv("REDISCLOUD_URL", "redis://localhost:6379")

conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        queues = [
            Queue(name=name, default_timeout=DEFAULT_QUEUE_TIMEOUT) for name in listen
        ]
        worker = Worker(queues=queues)
        worker.work()
