from typing import Optional
from client.api_client import ApiClient
from models.api_types import ApiResponse
from models.playlist_types import PlaylistResponseWrapper, PlaylistItemType
from utils.api_utils import deserialize_api_response

client = ApiClient()


def get_playlist(id: int) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    data = client.get(f"/playlist/{id}")
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


# wip
def update_playlist(id: int) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    data = client.get(f"/playlist/{id}")
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def add_item_to_playlist(
    playlist_id: int, type: PlaylistItemType, id: int
) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    form = {"type": type.value, "id": id}
    data = client.put(f"/playlist/{playlist_id}/add-item", form)
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def delete_item_from_playlist(
    playlist_id: int,
    playlist_item_id: int,
) -> Optional[ApiResponse[ApiResponse]]:
    data = client.delete(f"/playlist/{playlist_id}/remove-item/{playlist_item_id}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success


def delete_playlist(id: int) -> Optional[ApiResponse[ApiResponse]]:
    data = client.delete(f"/playlist/{id}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success
