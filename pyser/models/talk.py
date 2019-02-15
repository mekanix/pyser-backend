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
    end = DateTimeField(formats=[datetime_format], null=True)
    hall = TextField(null=True)
    published = BooleanField(default=False)
    start = DateTimeField(formats=[datetime_format], null=True)
    title = TextField()
    type = TextField()
    duration = IntegerField()
    user = ForeignKeyField(User, related_name='talks')
    event = ForeignKeyField(Event, related_name='talks')
