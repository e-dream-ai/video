from typing import Optional
from client.api_client import ApiClient
from models.api_types import ApiResponse
from models.dream_types import Dream
from models.playlist_types import (
    PlaylistResponseWrapper,
    PlaylistItemType,
    UpdatePlaylistRequest,
)
from controllers.file_upload import upload_file
from utils.api_utils import deserialize_api_response
from dataclasses import asdict

client = ApiClient()


def get_playlist(id: int) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Retrieves a playlist by its id
    Args:
        id (int): playlist id
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    data = client.get(f"/playlist/{id}")
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def update_playlist(
    playlist_id: int, request_data: UpdatePlaylistRequest
) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Updates a playlist by its id
    Args:
        playlist_id (int): playlist id
        request_data (UpdatePlaylistRequest): playlist data
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    request_data_dict = asdict(request_data)
    data = client.put(f"/playlist/{playlist_id}", request_data_dict)
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def add_item_to_playlist(
    playlist_id: int, type: PlaylistItemType, id: int
) -> Optional[ApiResponse[PlaylistResponseWrapper]]:
    """
    Adds item to a playlist
    Args:
        playlist_id (int): playlist id
        type (PlaylistItemType): item type
        id (int): item id
    Returns:
        Optional[ApiResponse[PlaylistResponseWrapper]]: An `ApiResponse` object containing a `PlaylistResponseWrapper`
    """
    form = {"type": type.value, "id": id}
    data = client.put(f"/playlist/{playlist_id}/add-item", form)
    response = deserialize_api_response(data, PlaylistResponseWrapper)
    playlist = response.data.playlist
    return playlist


def add_file_to_playlist(playlist_id: int, file_path: str) -> Optional[Dream]:
    """
    Adds a file to a playlist creating a dream
    Args:
        playlist_id (int): playlist id
        file_path (str): video file path
    Returns:
        Optional[Dream]: Created Dream
    """
    dream = upload_file(file_path)
    add_item_to_playlist(
        playlist_id=playlist_id, type=PlaylistItemType.DREAM, id=dream.id
    )
    return dream


def delete_item_from_playlist(
    playlist_id: int,
    playlist_item_id: int,
) -> Optional[ApiResponse]:
    """
    Deletes item from a playlist
    Args:
        playlist_id (int): playlist id
        playlist_item_id (int): playlist item id
    Returns:
        Optional[ApiResponse]: An `ApiResponse` object
    """
    data = client.delete(f"/playlist/{playlist_id}/remove-item/{playlist_item_id}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success


def delete_playlist(playlist_id: int) -> Optional[ApiResponse]:
    """
    Deletes a playlist
    Args:
        playlist_id (int): playlist id
    Returns:
        Optional[ApiResponse]: An `ApiResponse` object
    """
    data = client.delete(f"/playlist/{playlist_id}")
    response = deserialize_api_response(data, ApiResponse)
    return response.success
