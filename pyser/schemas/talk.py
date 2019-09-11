import datetime
from copy import copy

from marshmallow import fields, pre_dump

from ..date import datetime_format, peewee_datetime_format
from .auth import UserSchema
from .base import BaseSchema
from .event import EventSchema


class TalkSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    description = fields.String(description='Short talk description')
    duration = fields.Integer(description='duration')
    end = fields.DateTime(format=datetime_format, dump_only=True)
    event = fields.Nested(EventSchema, dump_only=True)
    hall = fields.String(description='Hall name')
    published = fields.Boolean()
    start = fields.DateTime(format=datetime_format)
    text = fields.String(description='Long talk description')
    title = fields.String(description='Talk title')
    user = fields.Nested(UserSchema, dump_only=True)
    video = fields.String(description='Talk video')

    @pre_dump
    def convert_date(self, data):
        duration = getattr(data, 'duration', None)
        newdata = copy(data)
        if isinstance(data.start, str):
            newdata.start = datetime.datetime.strptime(
                data.start,
                peewee_datetime_format
            )
        if None not in [duration, newdata.start]:
            newdata.end = newdata.start + datetime.timedelta(minutes=duration)
        return newdata
