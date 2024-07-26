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
    delete_item_from_playlist,
    delete_playlist,
)

from models.playlist_types import PlaylistItemType


def run():
    # user
    # get_logged_user()

    # dream
    # get_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # get_dream_vote("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # upvote_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # downvote_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")
    # delete_dream("02ff0d31-7b35-4e6a-ac18-5b114897aa0b")

    # playlist
    # get_playlist(32)
    # add_item_to_playlist(playlistId=32, type=PlaylistItemType.DREAM, id=357)
    # delete_item_from_playlist(playlist_id=32, playlist_item_id=206)
    pass


run()
