import sys

from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema
from freenit.schemas.user import UserSchema
from marshmallow import fields

from ..date import datetime_format


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
    slug = fields.String(description='Slug', dump_only=True)
    title = fields.String(description='Title')


PageOutSchema(BlogSchema, sys.modules[__name__])
