import datetime
from copy import copy

from marshmallow import fields, pre_dump

from ..date import datetime_format, peewee_datetime_format
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

    @pre_dump
    def convert_date(self, data):
        date = getattr(data, 'date', None)
        if date is None:
            return data
        if (type(data.date) == str):
            newdata = copy(data)
            newdata.date = datetime.datetime.strptime(
                data.date,
                peewee_datetime_format
            )
            return newdata
        return data
