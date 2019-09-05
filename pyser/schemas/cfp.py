from marshmallow import fields

from .auth import UserSchema
from .base import BaseSchema
from .talk import TalkSchema


class CfPSchema(BaseSchema):
    person = fields.Nested(UserSchema)
    talk = fields.Nested(TalkSchema)
