from marshmallow import fields

from .base import BaseSchema
from .event import EventSchema


class GalleryFileSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    filename = fields.String(description='Filename')


class GalleryAlbumSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    name = fields.String(description='Album name')
    files = fields.List(fields.Nested(GalleryFileSchema), many=True)
    event = fields.Nested(EventSchema, dump_only=True)
