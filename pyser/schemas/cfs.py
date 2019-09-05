from marshmallow import fields

from .base import BaseSchema
from .event import EventSchema


class CfSSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    email = fields.Email(description='CfS email')
    organization = fields.String(description='CfS organization')
    message = fields.String(description='CfS Message')
    event = fields.Nested(EventSchema, dump_only=True)
