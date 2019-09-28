from marshmallow import fields

from .base import BaseSchema
from .event import EventSchema


class GalleryFileSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    filename = fields.String(description='Filename')


class GalleryFilePaginatedSchema(BaseSchema):
    data = fields.List(fields.Nested(GalleryFileSchema))
    pages = fields.Number()
    total = fields.Number()


class GalleryAlbumSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    name = fields.String(description='Album name')
    prefix = fields.String(description='Prefix')
    files = fields.Nested(GalleryFilePaginatedSchema)
    event = fields.Nested(EventSchema, dump_only=True)
