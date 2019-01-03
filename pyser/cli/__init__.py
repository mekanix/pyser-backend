import click

from flask.cli import AppGroup
from peewee import IntegrityError
from peewee_migrate import Router
from pyser.models.event import Event
from pyser.models.gallery import GalleryAlbum

events = AppGroup('events')
migration = AppGroup('migration')


def registerEvents(app):
    @events.command()
    @click.argument('year')
    def create(year):
        try:
            event = Event(year=int(year), published=True)
            event.save()
            album = GalleryAlbum(event=event, name='main')
            album.save()
        except IntegrityError as e:
            print(e)
            print('Default event and gallery album already exist')


def registerMigration(app):
    router = Router(app.db.database)

    @migration.command()
    def list():
        for migration in router.done:
            print(migration)

    @migration.command()
    @click.argument('name')
    def create(name):
        router.create(name, 'pyser.models')

    @migration.command()
    def run():
        router.run()


def register(app):
    registerEvents(app)
    registerMigration(app)
    app.cli.add_command(events)
    app.cli.add_command(migration)
