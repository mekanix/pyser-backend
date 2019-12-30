from freenit.schemas.base import BaseSchema
from freenit.schemas.user import UserSchema
from marshmallow import fields

from .talk import TalkSchema


class CfPSchema(BaseSchema):
    person = fields.Nested(UserSchema)
    talk = fields.Nested(TalkSchema)
