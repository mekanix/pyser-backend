import sys

from freenit.schemas.base import BaseSchema
from freenit.schemas.paging import PageOutSchema
from marshmallow import fields

from .event import EventSchema


class CfSSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    email = fields.Email(description='CfS email')
    organization = fields.String(description='CfS organization')
    message = fields.String(description='CfS Message')
    event = fields.Nested(EventSchema, dump_only=True)


PageOutSchema(CfSSchema, sys.modules[__name__])
