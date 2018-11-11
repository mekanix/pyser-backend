from peewee import ForeignKeyField, TextField

from ..db import db
from .auth import User

Model = db.Model


class Talk(Model):
    description = TextField()
    text = TextField()
    title = TextField()
    user = ForeignKeyField(User, related_name='talks')
