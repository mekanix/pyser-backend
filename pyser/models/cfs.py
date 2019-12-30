from freenit.db import db
from peewee import ForeignKeyField, TextField

from .event import Event

Model = db.Model


class CfS(Model):
    email = TextField()
    organization = TextField()
    message = TextField()
    event = ForeignKeyField(Event, backref='cfs')
