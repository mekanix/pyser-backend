from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename

from ..models.event import Event
from ..models.gallery import GalleryAlbum, GalleryFile
from ..schemas.gallery import GalleryAlbumSchema, GalleryUpload
from ..schemas.paging import PageInSchema, PageOutSchema, paginate

blueprint = Blueprint('gallery', 'gallery')


@blueprint.route('', endpoint='albums')
@blueprint.route('/<int:year>', endpoint='year_albums')
class GalleryAlbumListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(GalleryAlbumSchema))
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

    @blueprint.arguments(GalleryUpload, location='files')
    @blueprint.response(GalleryUpload)
    def post(self, args, name, year=None):
        """Upload picture to album"""
        print(args)
        if year is not None:
            try:
                event = Event.get(year=year)
            except Event.DoesNotExist:
                abort(404, message='No such event')
        else:
            event = None
        #  print(secure_filename(args['file'].filename))
        try:
            album = GalleryAlbum.get(name=name, event=event)
        except GalleryAlbum.DoesNotExist:
            abort(404, message='No such album')
        return {}
