from peewee import ForeignKeyField, TextField

from ..db import db
from .event import Event

Model = db.Model


class CfS(Model):
    email = TextField()
    organization = TextField()
    message = TextField()
    event = ForeignKeyField(Event, related_name='cfs')
