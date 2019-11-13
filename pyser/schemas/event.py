import sys

from marshmallow import fields

from .base import BaseSchema
from .paging import PageOutSchema


class EventSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    year = fields.Integer(description='Year')
    published = fields.Boolean()


PageOutSchema(EventSchema, sys.modules[__name__])
