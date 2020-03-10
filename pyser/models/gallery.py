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
        name = self.album.name
        if self.album.event is None:
            return f'{prefix}/{name}/{self.filename}'
        year = self.album.event.year
        return f'{prefix}/{year}/{name}/{self.filename}'
