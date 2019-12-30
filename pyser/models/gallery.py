from freenit.db import db
from peewee import ForeignKeyField, TextField

from .event import Event

Model = db.Model


class GalleryAlbum(Model):
    event = ForeignKeyField(Event, backref='albums', null=True)
    name = TextField(index=True)


class GalleryFile(Model):
    album = ForeignKeyField(GalleryAlbum, backref='files')
    filename = TextField(index=True)

    def url(self, prefix=''):
        year = self.album.event.year
        name = self.album.name
        return f'{prefix}/{year}/{name}/{self.filename}'

    def path(self, prefix):
        year = self.album.event.year
        name = self.album.name
        return f'{prefix}/{year}/{name}/{self.filename}'
