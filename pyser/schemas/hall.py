import sys

from marshmallow import fields
from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema

from .event import EventSchema


class HallSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    name = fields.String(description='Hall name')
    event = fields.Nested(EventSchema, dump_only=True)


PageOutSchema(HallSchema, sys.modules[__name__])
