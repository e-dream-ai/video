import os
import boto3
import multiprocessing
from dotenv import load_dotenv
from multiprocessing.pool import ThreadPool
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
    print(f"processing uuid: {uuid}")
    process_video(group_id, uuid)


def app():
    print("Listening queue")
    cpu_count = (
        multiprocessing.cpu_count() if is_production or is_stage else DEFAULT_CPU_COUNT
    )
    pool = ThreadPool(processes=cpu_count)
    while True:
        results = []
        print("Empty results")

        try:
            messages = sqs_queue.receive_messages(
                AttributeNames=["MessageGroupId"],
                MessageAttributeNames=[
                    ProcessVideoQueueProperties.UUID,
                    ProcessVideoQueueProperties.VIDEO,
                ],
                MaxNumberOfMessages=cpu_count,
            )
            for message in messages:
                print("new message ---->", message)
                result = pool.apply_async(
                    process_message,
                    args=(message,),
                )
                results.append(result)
                # print(result.get())
                message.delete()

            ready = [result.ready() for result in results]
            successful = [result.successful() for result in results]
            print(results)

            # exit loop if all tasks returned success
            if all(successful):
                continue
            # raise exception reporting exceptions received from workers
            if all(ready) and not all(successful):
                raise Exception(
                    f"Workers raised following exceptions {[result._value for result in results if not result.successful()]}"
                )

            # close the thread pool
            # pool.close()
            # wait for all tasks to finish
            # pool.join()
            print(results)

        except Exception as e:
            print("Exception occurred")
            print(e)


if __name__ == "__main__":
    app()
