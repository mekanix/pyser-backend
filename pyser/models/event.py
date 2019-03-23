from peewee import BooleanField, IntegerField

from ..db import db

Model = db.Model


class Event(Model):
    year = IntegerField(index=True, unique=True)
    published = BooleanField()
