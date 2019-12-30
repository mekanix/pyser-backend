import sys

from flask_smorest.fields import Upload
from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema
from marshmallow import fields

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


class GalleryUploadSchema(BaseSchema):
    file = Upload(load_only=True)
    filename = fields.String(dump_only=True)


class ResumableGalleryUploadSchema(BaseSchema):
    resumableChunkNumber = fields.Integer()
    resumableChunkSize = fields.Integer()
    resumableCurrentChunkSize = fields.Integer()
    resumableFilename = fields.String()
    resumableIdentifier = fields.String()
    resumableRelativePath = fields.String()
    resumableTotalChunks = fields.Integer()
    resumableTotalSize = fields.Integer()
    resumableType = fields.String()


PageOutSchema(GalleryAlbumSchema, sys.modules[__name__])
