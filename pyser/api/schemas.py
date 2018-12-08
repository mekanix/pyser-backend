from flask_restplus import fields as rest_fields
from flask_restplus.model import Model
from marshmallow import Schema, fields, missing, post_load, pre_load
from marshmallow.exceptions import ValidationError

from ..models.auth import Role, User, UserRoles
from ..models.date import datetime_format
from ..models.event import MainEvent
from ..models.gallery import GalleryAlbum, GalleryFile
from ..models.parsing import TokenModel
from ..models.talk import Talk


def marshmallowToField(field, required=None):
    typeOfField = type(field)
    subtype = None
    if typeOfField in [fields.Email, fields.String, fields.UUID]:
        field_type = rest_fields.String
    elif typeOfField in [fields.Bool, fields.Boolean]:
        field_type = rest_fields.Boolean
    elif typeOfField in [fields.Int, fields.Integer]:
        field_type = rest_fields.Integer
    elif typeOfField == fields.DateTime:
        field_type = rest_fields.DateTime
    elif typeOfField == fields.Nested:
        field_type = rest_fields.Nested
        subtype = field.nested.fields()
    elif typeOfField == fields.List:
        field_type = rest_fields.List
        subtype = marshmallowToField(field.container)
    else:
        raise ValueError('Unknown field of type {}'.format(typeOfField))
    description = field.metadata.get('description', None)
    if required is None:
        field_required = field.required
    else:
        field_required = required
    if subtype is None:
        if field.default is missing:
            return field_type(
                description=description,
                required=field_required,
            )
        return field_type(
            description=description,
            required=field_required,
            default=field.default,
        )
    return field_type(
        subtype,
        description=description,
        required=field_required,
    )


class BaseSchema(Schema):
    @pre_load
    def check_payload(self, data):
        if data is None:
            raise ValidationError('Invalid input', field_names='message')
        return data

    @post_load
    def make_object(self, data):
        return self.Meta.model(**data)

    @classmethod
    def fields(cls, required=None):
        marshal_fields = {}
        for name in cls._declared_fields.keys():
            field = cls._declared_fields[name]
            if field.dump_only:
                continue
            marshal_fields[name] = marshmallowToField(field)
        return Model(cls.Meta.name, marshal_fields)


class TokenSchema(BaseSchema):
    email = fields.Email(required=True, description='Email')
    password = fields.Str(required=True, description='Password')

    class Meta:
        model = TokenModel
        name = 'Token'


class RoleSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    description = fields.String(required=True, description='Description')
    name = fields.String(required=True, description='Name')

    class Meta:
        model = Role
        name = 'Role'


class UserRolesSchema(BaseSchema):
    role = fields.Nested(RoleSchema)

    class Meta:
        model = UserRoles
        name = 'UserRoles'


class UserSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    active = fields.Boolean(description='Activate the user', default=True)
    admin = fields.Boolean(description='Is the user admin?', default=False)
    email = fields.Email(required=True, description='Email')
    password = fields.Str(
        required=True,
        description='Password',
        load_only=True
    )
    roles = fields.List(fields.Nested(UserRolesSchema), many=True)
    confirmed_at = fields.DateTime(
        description='Time when user was confirmed',
        dump_only=True,
    )

    class Meta:
        model = User
        name = 'User'


class TalkSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    description = fields.String(description='Short talk description')
    end = fields.DateTime(format=datetime_format)
    published = fields.Boolean(default=False)
    start = fields.DateTime(format=datetime_format)
    text = fields.String(description='Long talk description')
    title = fields.String(description='Talk title')
    user = fields.Nested(UserSchema)

    class Meta:
        model = Talk
        name = 'Talk'


class MainEventSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    year = fields.Integer(description='Year')

    class Meta:
        model = MainEvent
        name = 'MainEvent'


class GalleryFileSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    filename = fields.String(description='Filename')

    class Meta:
        model = GalleryFile
        name = 'GalleryFile'


class GalleryAlbumSchema(BaseSchema):
    id = fields.Integer(description='ID', dump_only=True)
    name = fields.String(description='Album name')
    files = fields.List(fields.Nested(GalleryFileSchema), many=True)
    mainEvent = fields.Nested(MainEventSchema)

    class Meta:
        model = GalleryAlbum
        name = 'GalleryAlbum'


schemas = [
    GalleryAlbumSchema,
    GalleryFileSchema,
    MainEventSchema,
    RoleSchema,
    TalkSchema,
    TokenSchema,
    UserRolesSchema,
    UserSchema,
]
