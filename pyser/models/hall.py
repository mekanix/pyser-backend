from peewee import ForeignKeyField, TextField

from ..db import db
from .event import Event

Model = db.Model


class Hall(Model):
    name = TextField()
    event = ForeignKeyField(Event, backref='halls')
