import sys

from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema
from marshmallow import fields


class EventSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    year = fields.Integer(description='Year')
    published = fields.Boolean()


PageOutSchema(EventSchema, sys.modules[__name__])
