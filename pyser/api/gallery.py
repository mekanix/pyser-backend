from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, reqparse

from ..models.event import MainEvent
from ..models.gallery import GalleryAlbum
from .namespaces import ns_gallery
from .pagination import paginate, parser
from .schemas import GalleryAlbumSchema, GalleryFileSchema

gallery_parser = reqparse.RequestParser()
gallery_parser.add_argument('resumableChunkNumber', type=int)
gallery_parser.add_argument('resumableChunkSize', type=int)
gallery_parser.add_argument('resumableCurrentChunkSize', type=int)
gallery_parser.add_argument('resumableTotalSize', type=int)
gallery_parser.add_argument('resumableType')
gallery_parser.add_argument('resumableIdentifier')
gallery_parser.add_argument('resumableType')
gallery_parser.add_argument('resumableRelativePath')


@ns_gallery.route('', endpoint='albums')
@ns_gallery.route('/<int:year>', endpoint='year_albums')
class GalleryAlbumListAPI(Resource):
    @ns_gallery.expect(parser)
    def get(self, year=None):
        """Get list of albums"""
        if year is None:
            return paginate(
                GalleryAlbum.select().where(
                    GalleryAlbum.mainEvent == None  # noqa: E711
                ),
                GalleryAlbumSchema(),
            )
        try:
            mainEvent = MainEvent.get(year=year)
        except MainEvent.DoesNotExist:
            return {'message': 'No such event'}, 404
        return paginate(mainEvent.albums, GalleryAlbumSchema())

    @jwt_required
    @ns_gallery.expect(GalleryAlbumSchema.fields())
    def post(self, year=None):
        """Create new album"""
        schema = GalleryAlbumSchema()
        album, errors = schema.load(request.get_json())
        if errors:
            return errors, 409
        album.mainEvent = None
        if year is not None:
            try:
                album.mainEvent = MainEvent.get(year=year)
            except MainEvent.DoesNotExist:
                return {'message': 'No such event'}, 404
        try:
            GalleryAlbum.get(name=album.name, mainEvent=album.mainEvent)
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
                mainEvent = MainEvent.get(year=year)
            except MainEvent.DoesNotExist:
                return {'message': 'No such event'}, 404
        else:
            mainEvent = None
        try:
            album = GalleryAlbum.get(name=name, mainEvent=mainEvent)
        except GalleryAlbum.DoesNotExist:
            return {'message': 'No such album'}, 404
        schema = GalleryAlbumSchema()
        response, errors = schema.dump(album)
        if errors:
            return errors, 409
        files = paginate(album.files, GalleryFileSchema())
        response['files'] = files['data']
        response['pages'] = files['pages']
        response['total'] = files['total']
        prefix = current_app.config.get('MEDIA_URL', None)
        if prefix is None:
            return {'message': 'Backend missconfiguration, no MEDIAL_URL'}, 409
        response['prefix'] = prefix
        return response

    @jwt_required
    @ns_gallery.expect(gallery_parser)
    def post(self, name, year=None):
        """Upload new file"""
        if year is not None:
            try:
                mainEvent = MainEvent.get(year=year)
            except MainEvent.DoesNotExist:
                return {'message': 'No such event'}, 404
        else:
            mainEvent = None
        try:
            GalleryAlbum.get(name=name, mainEvent=mainEvent)
        except GalleryAlbum.DoesNotExist:
            return {'message': 'No such album'}, 404
        args = gallery_parser.parse_args()
        print(args)
        return {'message': 'OK'}
