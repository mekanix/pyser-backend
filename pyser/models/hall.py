from freenit.db import db
from peewee import ForeignKeyField, TextField

from .event import Event

Model = db.Model


class Hall(Model):
    name = TextField()
    event = ForeignKeyField(Event, backref='halls')
