from peewee import ForeignKeyField, TextField

from ..db import db
from .event import MainEvent

Model = db.Model


class GalleryAlbum(Model):
    mainEvent = ForeignKeyField(MainEvent, related_name='albums', null=True)
    name = TextField(index=True)


class GalleryFile(Model):
    album = ForeignKeyField(GalleryAlbum, related_name='files')
    filename = TextField(index=True)

    @property
    def url(self):
        return f'/media/{self.mainEvent.year}/${self.filename}'
