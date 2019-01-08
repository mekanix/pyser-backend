from peewee import BooleanField, IntegerField, TextField

from ..db import db

Model = db.Model


class Event(Model):
    year = IntegerField(index=True, unique=True)
    published = BooleanField(default=False)
    mainHall = TextField()
