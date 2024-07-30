from controllers.user import get_logged_user
from controllers.dream import (
    get_dream,
    update_dream,
    get_dream_vote,
    upvote_dream,
    downvote_dream,
    delete_dream,
)
from controllers.playlist import (
    get_playlist,
    update_playlist,
    add_item_to_playlist,
    add_file_to_playlist,
    delete_item_from_playlist,
    delete_playlist,
)
from controllers.file_upload import upload_file
from models.playlist_types import PlaylistItemType, UpdatePlaylistRequest
from models.dream_types import UpdateDreamRequest


def run():
    # user
    # get_logged_user()

    # dream
    # get_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # get_dream_vote("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # update_dream(
    #     "02ff0d31-7b35-4e6a-ac18-5b114897aa0b",
    #     request_data=UpdateDreamRequest(name="name python"),
    # )
    # upvote_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # downvote_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # delete_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")

    # playlist
    # get_playlist(32)
    # update_playlist(
    #     32,
    #     request_data=UpdatePlaylistRequest(name="name python"),
    # )
    # add_item_to_playlist(playlistId=32, type=PlaylistItemType.DREAM, id=357)
    # delete_item_from_playlist(playlist_id=32, playlist_item_id=206)
    # add_file_to_playlist(
    #     playlist_id=32,
    #     file_path="path_to_file/python_video.mp4",
    # )
    # delete_playlist(32)

    # file
    # upload_file("path_to_file/python_video.mp4")
    pass


run()
