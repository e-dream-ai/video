from marshmallow import Schema, fields, validate, ValidationError

ALLOWED_VIDEO_TYPES = [
    "mp4",
    "avi",
    "mov",
    "wmv",
    "mkv",
    "flv",
    "mpeg",
    "webm",
    "ogv",
    "3gp",
    "3g2",
    "h264",
    "hevc",
    "divx",
    "xvid",
    "avchd",
]


class VideoProcessSchema(Schema):
    dream_uuid = fields.Str(required=True, validate=[validate.Length(equal=36)])
    extension = fields.Str(
        required=True, validate=[validate.OneOf(ALLOWED_VIDEO_TYPES)]
    )


class VideoMd5Schema(Schema):
    dream_uuid = fields.Str(required=True, validate=[validate.Length(equal=36)])


class VideoFilmstripSchema(Schema):
    dream_uuid = fields.Str(required=True, validate=[validate.Length(equal=36)])


class ProcessGeneratedVideoSchema(Schema):
    dream_uuid = fields.Str(required=True, validate=[validate.Length(equal=36)])
    video_url = fields.Str(required=True)
