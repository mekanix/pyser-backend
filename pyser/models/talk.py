from peewee import (
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    TextField,
    IntegerField,
)

from ..date import datetime_format
from ..db import db
from .auth import User
from .event import Event

Model = db.Model


class Talk(Model):
    description = TextField()
    duration = IntegerField()
    event = ForeignKeyField(Event, related_name='talks')
    hall = TextField(null=True)
    published = BooleanField()
    start = DateTimeField(formats=[datetime_format], null=True)
    title = TextField()
    type = TextField()
    user = ForeignKeyField(User, related_name='talks')
