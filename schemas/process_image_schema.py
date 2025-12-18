from marshmallow import Schema, fields, validate

ALLOWED_IMAGE_TYPES = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "webp",
    "tiff",
    "svg",
    "ico",
    "heif",
    "heic",
]


class ImageProcessSchema(Schema):
    dream_uuid = fields.Str(required=True, validate=[validate.Length(equal=36)])
    extension = fields.Str(
        required=True, validate=[validate.OneOf(ALLOWED_IMAGE_TYPES)]
    )

