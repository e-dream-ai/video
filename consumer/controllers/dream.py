from typing import Optional
from client.api_client import ApiClient
from models.api_types import ApiResponse
from models.dream_types import DreamResponseWrapper, DreamVoteResponseWrapper
from utils.api_utils import deserialize_api_response

client = ApiClient()


def get_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    data = client.get(f"/dream/{uuid}")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


# wip
def update_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    data = client.put(f"/dream/{uuid}")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def get_dream_vote(uuid: str) -> Optional[ApiResponse[DreamVoteResponseWrapper]]:
    data = client.get(f"/dream/{uuid}/vote")
    response = deserialize_api_response(data, DreamVoteResponseWrapper)
    vote = response.data.vote
    return vote


def upvote_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    data = client.put(f"/dream/{uuid}/upvote")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def downvote_dream(uuid: str) -> Optional[ApiResponse[DreamResponseWrapper]]:
    data = client.put(f"/dream/{uuid}/downvote")
    response = deserialize_api_response(data, DreamResponseWrapper)
    dream = response.data.dream
    return dream


def delete_dream(uuid: str) -> Optional[ApiResponse[ApiResponse]]:
    data = client.delete(f"/dream/{uuid}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success
