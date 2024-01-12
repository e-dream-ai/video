import os
import boto3
import multiprocessing
from dotenv import load_dotenv
from utils.process_video import process_video
from api.dream_api import set_dream_processing, set_dream_processed

load_dotenv()

DEFAULT_CPU_COUNT = 4
AWS_REGION = os.getenv("AWS_REGION")
AWS_SQS_NAME = os.getenv("AWS_SQS_NAME")
is_production = os.getenv("ENV") == "production"
is_stage = os.getenv("ENV") == "stage"


class ProcessVideoQueueProperties:
    UUID = "UUID"
    VIDEO = "VIDEO"
    USER_UUID = "USER_UUID"


sqs = boto3.resource("sqs", region_name=AWS_REGION)
sqs_queue = sqs.get_queue_by_name(QueueName=AWS_SQS_NAME)
cpu_count = (
    multiprocessing.cpu_count() if is_production or is_stage else DEFAULT_CPU_COUNT
)


def worker():
    print(f"Process ID: {multiprocessing.current_process().pid}")
    while True:
        messages = sqs_queue.receive_messages(
            AttributeNames=["MessageGroupId"],
            MessageAttributeNames=[
                ProcessVideoQueueProperties.UUID,
                ProcessVideoQueueProperties.VIDEO,
                ProcessVideoQueueProperties.USER_UUID,
            ],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
        )
        if len(messages):
            process_message(messages[0])
            messages[0].delete()


def process_message(message):
    message_body = message.body
    message_attributes = message.message_attributes
    uuid = message_attributes[ProcessVideoQueueProperties.UUID]["StringValue"]
    user_uuid = message_attributes[ProcessVideoQueueProperties.USER_UUID]["StringValue"]
    print("-----------")
    print(f"processing uuid: {message_body}")
    set_dream_processing(uuid)
    process_video(user_uuid, uuid)
    set_dream_processed(uuid)


def app():
    print("Listening queue")

    processes = []

    # Create and start processes
    for _ in range(cpu_count):
        p = multiprocessing.Process(target=worker)
        p.start()
        processes.append(p)

    try:
        # Keep the main program running
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Terminating processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
    except Exception as e:
        print("Exception occurred")
        print(e)
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


if __name__ == "__main__":
    app()
