from peewee import IntegerField

from ..db import db

Model = db.Model


class MainEvent(Model):
    year = IntegerField()
