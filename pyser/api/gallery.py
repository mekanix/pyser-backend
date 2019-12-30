import os
from tempfile import NamedTemporaryFile

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from freenit.schemas.paging import PageInSchema, paginate
from werkzeug.utils import secure_filename

from ..models.event import Event
from ..models.gallery import GalleryAlbum, GalleryFile
from ..schemas.gallery import (
    GalleryAlbumPageOutSchema,
    GalleryAlbumSchema,
    GalleryUploadSchema,
    ResumableGalleryUploadSchema
)

blueprint = Blueprint('gallery', 'gallery')

chunks = {}


@blueprint.route('', endpoint='albums')
@blueprint.route('/<int:year>', endpoint='year_albums')
class GalleryAlbumListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumPageOutSchema)
    def get(self, pagination, year=None):
        """Get list of albums"""
        if year is None:
            return paginate(
                GalleryAlbum.select().where(GalleryAlbum.event),
                pagination,
            )
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='No such event')
        return paginate(event.albums, pagination)


@blueprint.route('/album/<name>', endpoint='album')
@blueprint.route('/album/<name>/<int:year>', endpoint='year_album')
class GalleryAlbumAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(GalleryAlbumSchema)
    def get(self, pagination, name, year=None):
        """Get album details"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                abort(404, message='No such event')
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        album.files = paginate(
            album.files.order_by(GalleryFile.filename),
            pagination,
        )
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        album.prefix = prefix
        return album

    @blueprint.arguments(GalleryUploadSchema, location='files')
    @blueprint.arguments(ResumableGalleryUploadSchema, location='form')
    @blueprint.response(ResumableGalleryUploadSchema)
    def post(self, fileargs, formargs, name, year=None):
        """Upload picture to album"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                abort(404, message='No such event')
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        album.prefix = current_app.config.get('MEDIA_URL', None)
        if album.prefix is None:
            abort(409, message='Backend misconfiguration, no MEDIAL_URL')
        uploadFile = fileargs['file']
        chunkNumber = formargs['resumableChunkNumber']
        identifier = formargs['resumableIdentifier']
        fileEntry = chunks.get(identifier, None)
        media_path = os.path.abspath(
            current_app.config.get(
                'MEDIA_PATH',
                None,
            )
        )
        if fileEntry is None:
            tempfile = NamedTemporaryFile(
                dir=f'{media_path}/tmp',
                delete=False
            )
            tempfile.close()
            fileEntry = {
                'chunkSize': formargs['resumableChunkSize'],
                'filename': formargs['resumableFilename'],
                'identifier': identifier,
                'temp': tempfile.name,
                'total': formargs['resumableTotalChunks'],
                'type': formargs['resumableType'],
            }
            chunks[identifier] = fileEntry
            uploadFile.save(fileEntry['temp'])
        else:
            with open(fileEntry['temp'], 'ab') as tempfile:
                offset = (chunkNumber - 1) * fileEntry['chunkSize']
                tempfile.seek(offset)
                tempfile.write(uploadFile.read())

        if chunkNumber == fileEntry['total']:
            tempfile = fileEntry['temp']
            try:
                finalFile = GalleryFile.get(
                    album=album,
                    filename=secure_filename(uploadFile.filename),
                )
            except GalleryFile.DoesNotExist:
                finalFile = GalleryFile(
                    album=album,
                    filename=secure_filename(uploadFile.filename),
                )
            file_dir = f'{media_path}/{event.year}/{album.name}'
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            finalPath = finalFile.path(prefix=media_path)
            os.rename(tempfile, finalPath)
            os.chmod(finalPath, 0o644)
            finalFile.save()
        return formargs
