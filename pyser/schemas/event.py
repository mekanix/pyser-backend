from marshmallow import fields

from .base import BaseSchema


class EventSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    year = fields.Integer(description='Year')
    published = fields.Boolean()
