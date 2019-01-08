import click

from flask.cli import AppGroup
from flask_security.cli import users
from peewee import IntegrityError
from peewee_migrate import Router
from pyser.models.auth import User
from pyser.models.event import Event
from pyser.models.gallery import GalleryAlbum
from pyser.models.hall import Hall

events = AppGroup('events', help='Event operations')
migration = AppGroup('migration', help='Manage DB migrations')


def registerEvents(app):
    @events.command()
    @click.argument('year')
    def create(year):
        try:
            event = Event(year=int(year), published=True, mainHall='main')
            event.save()
        except IntegrityError as e:
            print('Default event already exists')
            return
        album = GalleryAlbum(event=event, name='main')
        album.save()
        hall = Hall(event=event, name='main')
        hall.save()

    app.cli.add_command(events)


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

    app.cli.add_command(migration)


def registerUser(app):
    @users.command()
    @click.argument('email')
    def admin(email):
        """Proclaim user an admin"""
        try:
            user = User.get(email=email)
            user.admin = True
            user.save()
        except User.DoesNotExist:
            print('No such user')

    @users.command()
    @click.argument('email')
    def deadmin(email):
        """Remove admin priviledges from user"""
        try:
            user = User.get(email=email)
            user.admin = False
            user.save()
        except User.DoesNotExist:
            print('No such user')


def register(app):
    registerEvents(app)
    registerMigration(app)
    registerUser(app)
