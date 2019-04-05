import os

from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, reqparse
from werkzeug.datastructures import FileStorage

from ..models.event import Event
from ..models.gallery import GalleryAlbum, GalleryFile
from .namespaces import ns_gallery
from .pagination import paginate, parser
from .resources import ProtectedResource
from .schemas import GalleryAlbumSchema, GalleryFileSchema

gallery_parser = reqparse.RequestParser()
gallery_parser.add_argument('resumableChunkNumber', type=int, location='form')
gallery_parser.add_argument('resumableChunkSize', type=int, location='form')
gallery_parser.add_argument(
    'resumableCurrentChunkSize',
    type=int,
    location='form'
)
gallery_parser.add_argument('resumableTotalSize', type=int, location='form')
gallery_parser.add_argument('resumableType', location='form')
gallery_parser.add_argument('resumableIdentifier', location='form')
gallery_parser.add_argument('resumableType', location='form')
gallery_parser.add_argument('resumableRelativePath', location='form')
gallery_parser.add_argument('file', type=FileStorage, location='files')


@ns_gallery.route('', endpoint='albums')
@ns_gallery.route('/<int:year>', endpoint='year_albums')
class GalleryAlbumListAPI(Resource):
    @ns_gallery.expect(parser)
    def get(self, year=None):
        """Get list of albums"""
        if year is None:
            return paginate(
                GalleryAlbum.select().where(GalleryAlbum.event),
                GalleryAlbumSchema(),
            )
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        return paginate(event.albums, GalleryAlbumSchema())

    @jwt_required
    @ns_gallery.expect(GalleryAlbumSchema.fields())
    def post(self, year=None):
        """Create new album"""
        schema = GalleryAlbumSchema()
        album, errors = schema.load(request.get_json())
        if errors:
            return errors, 409
        album.event = None
        if year is not None:
            try:
                album.event = Event.get(year=year)
            except Event.DoesNotExist:
                return {'message': 'No such event'}, 404
        try:
            GalleryAlbum.get(name=album.name, event=album.event)
            return {'message': 'Album already exists'}, 409
        except GalleryAlbum.DoesNotExist:
            album.save()
        response, errors = schema.dump(album)
        if errors:
            return errors, 409
        return response


@ns_gallery.route('/album/<name>', endpoint='album')
@ns_gallery.route('/album/<name>/<int:year>', endpoint='year_album')
class GalleryAlbumAPI(Resource):
    @ns_gallery.expect(parser)
    def get(self, name, year=None):
        """Get album details"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                return {'message': 'No such event'}, 404
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            return {'message': 'No such album'}, 404
        schema = GalleryAlbumSchema()
        response, errors = schema.dump(album)
        if errors:
            return errors, 409
        files = paginate(
            album.files.order_by(GalleryFile.filename),
            GalleryFileSchema(),
        )
        response['files'] = files['data']
        response['pages'] = files['pages']
        response['total'] = files['total']
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            return {'message': 'Backend missconfiguration, no MEDIAL_URL'}, 409
        response['prefix'] = prefix
        return response


@ns_gallery.route('/upload/<name>', endpoint='upload')
@ns_gallery.route('/upload/<name>/<int:year>', endpoint='year_upload')
class GalleryUploadAPI(ProtectedResource):
    @ns_gallery.expect(gallery_parser)
    def post(self, name, year=None):
        """Upload new file"""
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                return {'message': 'No such event'}, 404
        else:
            event = None
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            return {'message': 'No such album'}, 404
        args = gallery_parser.parse_args()
        file = args.get('file', None)
        if file is None:
            return {'message': 'File must be provided'}, 409
        media_path = os.path.abspath(
            current_app.config.get(
                'MEDIA_PATH',
                None,
            )
        )
        galleryFile, created = GalleryFile.get_or_create(
            album=album,
            filename=file.filename,
        )
        if created:
            chunkNumber = args.get('resumableChunkNumber')
            if chunkNumber == 1:
                galleryFile.save()
            filePath = galleryFile.path(media_path)
            dirPath = os.path.dirname(filePath)
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
        with open(galleryFile.path(media_path), 'ab+') as f:
            f.write(file.stream.read())
        return {'message': 'OK'}
