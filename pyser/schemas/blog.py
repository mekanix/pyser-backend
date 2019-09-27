from marshmallow import fields

from ..date import datetime_format
from .auth import UserSchema
from .base import BaseSchema


class BlogSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    author = fields.Nested(UserSchema, dump_only=True)
    content = fields.Str(description='Content')
    date = fields.DateTime(
        description='Time when blog was created',
        format=datetime_format,
        dump_only=True,
    )
    published = fields.Boolean(description='Published', default=False)
    slug = fields.Str(description='Slug', dump_only=True)
    title = fields.Str(description='Title')
