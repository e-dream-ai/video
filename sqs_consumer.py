import os
import boto3
import multiprocessing
from multiprocessing.pool import ThreadPool
from dotenv import load_dotenv
from process_video import process_video

load_dotenv()

DEFAULT_CPU_COUNT = 4
AWS_REGION = os.getenv("AWS_REGION")
AWS_SQS_NAME = os.getenv("AWS_SQS_NAME")
is_production = os.getenv("ENV") == "production"
is_stage = os.getenv("ENV") == "stage"


class ProcessVideoQueueProperties:
    UUID = "UUID"
    VIDEO = "VIDEO"


sqs = boto3.resource("sqs", region_name=AWS_REGION)
sqs_queue = sqs.get_queue_by_name(QueueName=AWS_SQS_NAME)


def process_message(message):
    message_body = message.body
    message_attributes = message.message_attributes
    attributes = message.attributes
    group_id = attributes["MessageGroupId"]
    uuid = message_attributes[ProcessVideoQueueProperties.UUID]["StringValue"]
    video = message_attributes[ProcessVideoQueueProperties.VIDEO]["StringValue"]
    print("-----------")
    print(f"processing message: {message_body}")
    print(f"processing group_id: {group_id}")
    print(f"processing uuid: {uuid}")
    print(f"processing video: {video}")
    process_video(group_id, uuid)


if __name__ == "__main__":
    print("Listening queue")
    cpu_count = (
        multiprocessing.cpu_count() if is_production or is_stage else DEFAULT_CPU_COUNT
    )
    while True:
        results = []
        print(results)

        try:
            pool = ThreadPool()
            messages = sqs_queue.receive_messages(
                AttributeNames=["MessageGroupId"],
                MessageAttributeNames=[
                    ProcessVideoQueueProperties.UUID,
                    ProcessVideoQueueProperties.VIDEO,
                ],
            )
            for message in messages:
                result = pool.apply_async(
                    process_message,
                    args=(message,),
                )
                results.append(result)
                print(result.get())
                message.delete()

            # [result.wait() for result in results]
            # close the thread pool
            pool.close()
            # wait for all tasks to finish
            pool.join()

        except Exception as e:
            print("Exception occurred")
            print(e)
