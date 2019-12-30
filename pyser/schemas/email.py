from marshmallow import fields

from freenit.schemas.base import BaseSchema


class EmailSchema(BaseSchema):
    fromAddress = fields.Str()
    to = fields.Str()
    subject = fields.Str()
    message = fields.Str()
