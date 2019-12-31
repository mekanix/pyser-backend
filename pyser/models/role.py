import peewee
from freenit.models.role import Role as BaseRole
from freenit.models.role import UserRoles as BaseUserRoles

from .user import User


class Role(BaseRole):
    pass


class UserRoles(BaseUserRoles):
    role = peewee.ForeignKeyField(Role, backref='users')
    user = peewee.ForeignKeyField(User, backref='roles')
