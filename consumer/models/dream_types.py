from enum import Enum
from typing import List, Optional, Dict, ByteString, Any
from dataclasses import dataclass
from .user_types import User


# Enum for DreamStatusType
class DreamStatusType(Enum):
    NONE = "none"
    QUEUE = "queue"
    PROCESSING = "processing"
    FAILED = "failed"
    PROCESSED = "processed"


# Data class for Dream
@dataclass
class Dream:
    id: int
    name: str
    activityLevel: int
    featureRank: int
    thumbnail: str
    displayedOwner: User
    user: User
    uuid: str
    video: str
    frontendUrl: Optional[str] = None
    original_video: Optional[str] = None
    processedVideoSize: Optional[int] = None
    processedVideoFrames: Optional[int] = None
    processedVideoFPS: Optional[int] = None
    status: DreamStatusType = DreamStatusType.NONE
    nsfw: Optional[bool] = None
    playlistItems: Any = None
    filmstrip: Optional[List[str]] = None
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None
    processed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


# Data class for PresignedPost
@dataclass
class PresignedPost:
    url: str
    uuid: str
    fields: Dict[str, str]


# Data class for PresignedPostRequest
@dataclass
class PresignedPostRequest:
    params: Optional[PresignedPost] = None
    file: Optional[ByteString] = None


# Data class for MultipartUpload
@dataclass
class MultipartUpload:
    urls: Optional[List[str]] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for RefreshMultipartUpload
@dataclass
class RefreshMultipartUpload:
    url: Optional[str] = None
    dream: Optional[Dream] = None
    uploadId: Optional[str] = None


# Data class for MultipartUploadRequest
@dataclass
class MultipartUploadRequest:
    presignedUrl: str
    filePart: ByteString
    partNumber: int
    totalParts: int
