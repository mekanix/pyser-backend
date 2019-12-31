import sys

from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema
from marshmallow import fields

from ..date import datetime_format
from .event import EventSchema
from .user import UserSchema


class TicketSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    canceled = fields.Boolean(description='Canceled', default=False)
    event = fields.Nested(EventSchema, dump_only=True)
    identifier = fields.String(description='Identifier')
    visitor = fields.Nested(UserSchema, dump_only=True)
    date = fields.DateTime(
        description='Time when blog was created',
        format=datetime_format,
        dump_only=True,
    )


PageOutSchema(TicketSchema, sys.modules[__name__])
