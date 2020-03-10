from flask.cli import AppGroup

from ..models.gallery import GalleryAlbum

gallery = AppGroup('gallery', short_help='Manage galleries')


def register_gallery(app):
    @gallery.command()
    def create():
        try:
            GalleryAlbum.get(name='avatars')
        except GalleryAlbum.DoesNotExist:
            avatars = GalleryAlbum(name='avatars')
            avatars.save()

    app.cli.add_command(gallery)


def register(app):
    register_gallery(app)
