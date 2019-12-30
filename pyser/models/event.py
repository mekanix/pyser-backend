from peewee import BooleanField, IntegerField

from freenit.db import db

Model = db.Model


class Event(Model):
    year = IntegerField(index=True, unique=True)
    published = BooleanField()
