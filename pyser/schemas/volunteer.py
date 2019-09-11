from marshmallow import fields

from .base import BaseSchema


class VolunteerCountSchema(BaseSchema):
    count = fields.Int()
    max = fields.Int()
