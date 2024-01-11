import os
import boto3
import multiprocessing
from dotenv import load_dotenv
from process_video import process_video

load_dotenv()

DEFAULT_CPU_COUNT = 4
AWS_REGION = os.getenv("AWS_REGION")
AWS_SQS_NAME = os.getenv("AWS_SQS_NAME")
is_production = os.getenv("ENV") == "production"


class ProcessVideoQueueProperties:
    UUID = "UUID"
    VIDEO = "VIDEO"


sqs = boto3.resource("sqs", region_name=AWS_REGION)
sqs_queue = sqs.get_queue_by_name(QueueName=AWS_SQS_NAME)


def process_message(message):
    message_body = message.body
    message_attributes = message.message_attributes
    group_id = message.group_id
    uuid = message_attributes[ProcessVideoQueueProperties.UUID]["StringValue"]
    video = message_attributes[ProcessVideoQueueProperties.VIDEO]["StringValue"]
    process_video(group_id, uuid)
    print(f"processing message: {message_body}")
    print(f"processing uuid: {group_id}")
    print(f"processing uuid: {uuid}")
    print(f"processing video: {video}")


if __name__ == "__main__":
    print("Listening queue")
    cpu_count = multiprocessing.cpu_count() if is_production else DEFAULT_CPU_COUNT
    pool = multiprocessing.Semaphore(cpu_count)
    while True:
        results = []

        try:
            messages = sqs_queue.receive_messages(
                MessageAttributeNames=[
                    ProcessVideoQueueProperties.UUID,
                    ProcessVideoQueueProperties.VIDEO,
                ]
            )
            for message in messages:
                result = pool.apply_async(
                    process_message,
                    args=(message),
                )
                results.append(result)
                message.delete()

            [result.wait() for result in results]

        except Exception:
            print("Exception occured")
            continue
