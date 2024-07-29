import requests
import time
import math
from typing import Optional, List
from dataclasses import asdict
from pathlib import Path
from models.file_upload_types import (
    CreateMultipartUploadFormValues,
    MultipartUpload,
    CompleteMultipartUploadFormValues,
    RefreshMultipartUpload,
    CompletedPart,
)
from models.dream_types import (
    DreamResponseWrapper,
)
from models.api_types import ApiResponse
from client.api_client import ApiClient
from utils.api_utils import deserialize_api_response

client = ApiClient()
part_size = 1024 * 1024 * 200  # 200 MB
retry_delay: float = 0.2
max_retries = 3


def calculate_total_parts(file_size: int) -> int:
    return max(math.ceil(file_size / part_size), 1)


def upload_file_request(
    presigned_url: str,
    file_part: bytes,
    file_type: Optional[str] = None,
) -> Optional[str]:
    headers = {"Content-Type": file_type or ""}
    try:
        response = requests.put(
            presigned_url,
            data=file_part,
            headers=headers,
        )
        response.raise_for_status()
        # Extract and clean the ETag header
        etag = response.headers.get("etag", "")
        cleaned_etag = etag.strip('"')
        return cleaned_etag
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def create_multipart_upload(
    request_data: CreateMultipartUploadFormValues,
) -> MultipartUpload:
    request_data_dict = asdict(request_data)
    data = client.post(f"/dream/create-multipart-upload", request_data_dict)
    response = deserialize_api_response(data, MultipartUpload)
    multipart_upload = response.data
    return multipart_upload


def refresh_multipart_upload_url(
    uuid: str,
    request_data: CompleteMultipartUploadFormValues,
) -> RefreshMultipartUpload:
    request_data_dict = asdict(request_data)
    data = client.post(f"/dream/{uuid}/refresh-multipart-upload-url", request_data_dict)
    response = deserialize_api_response(data, MultipartUpload)
    multipart_upload = response.data
    return multipart_upload


def upload_file_part(
    presigned_url: str,
    file_part: bytes,
    file_type: Optional[str] = None,
) -> Optional[str]:
    attempt = 0
    while attempt < max_retries:
        result = upload_file_request(presigned_url, file_part, file_type)
        if result is not None:
            return result
        else:
            print(f"Attempt {attempt + 1} failed.")
            attempt += 1
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise f"Upload failed. Max retries reached on part {file_part}"


def complete_multipart_upload(
    uuid: str,
    request_data: CompleteMultipartUploadFormValues,
) -> DreamResponseWrapper:
    request_data_dict = asdict(request_data)
    data = client.post(f"/dream/{uuid}/complete-multipart-upload", request_data_dict)
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def upload_file(file_path: str):
    path = Path(file_path)
    file_name = path.name
    file_extension = path.suffix.lstrip(".")
    file_size = path.stat().st_size
    total_parts = calculate_total_parts(file_size)

    multipart_upload: MultipartUpload = create_multipart_upload(
        CreateMultipartUploadFormValues(
            name=file_name, extension=file_extension, nsfw=False, parts=total_parts
        )
    )

    dream = multipart_upload.dream
    upload_id = multipart_upload.uploadId
    urls = multipart_upload.urls
    completed_parts: List[CompletedPart] = []

    with open(file_path, "rb") as file:
        while part_data := file.read(part_size):
            for index, url in enumerate(urls):
                print(f"Index {index}: {url}")
                part_number = index + 1
                etag = upload_file_part(
                    presigned_url=url, file_part=part_data, file_type=file_extension
                )
                completed_parts.append(CompletedPart(ETag=etag, PartNumber=part_number))

    complete_multipart_upload(
        dream.uuid,
        CompleteMultipartUploadFormValues(
            uploadId=upload_id,
            extension=file_extension,
            name=file_name,
            parts=completed_parts,
        ),
    )
