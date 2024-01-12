import os
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CPU_COUNT = 4
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

ACL = "public-read"
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


def download_file(file_name, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        s3_client.download_file(BUCKET_NAME, object_name, file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(file_name, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(
            file_name, BUCKET_NAME, object_name, ExtraArgs={"ACL": ACL}
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True
