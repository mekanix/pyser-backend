from freenit.db import db
from freenit.models.user import User
from peewee import (
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    TextField
)

from ..date import datetime_format
from .event import Event

Model = db.Model


class Talk(Model):
    description = TextField()
    duration = IntegerField()
    event = ForeignKeyField(Event, backref='talks')
    hall = TextField(null=True)
    published = BooleanField()
    start = DateTimeField(formats=[datetime_format], null=True)
    title = TextField()
    user = ForeignKeyField(User, backref='talks')
    video = TextField(null=True)
