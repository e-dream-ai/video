from typing import List, Optional
from dataclasses import dataclass
from models.dream_types import Dream
from models.user_types import User


# Data class for PlaylistItem
@dataclass
class PlaylistItem:
    id: int
    type: str
    order: int
    playlist: Optional["Playlist"] = None
    dreamItem: Optional[Dream] = None
    playlistItem: Optional["Playlist"] = None
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None


# Data class for Playlist
@dataclass
class Playlist:
    id: int
    name: str
    thumbnail: str
    updated_at: str
    user: User
    displayedOwner: User
    created_at: str
    items: Optional[List[PlaylistItem]] = None
    itemCount: Optional[int] = None
    featureRank: Optional[int] = None
    nsfw: Optional[bool] = None
