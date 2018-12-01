from flask_restplus import Resource

from ..models.event import MainEvent
from ..models.gallery import GalleryAlbum
from .namespaces import ns_gallery
from .pagination import paginate, parser
from .schemas import GalleryAlbumSchema


@ns_gallery.route('', endpoint='albums')
@ns_gallery.route('/<year>', endpoint='year_albums')
class GalleryAPI(Resource):
    @ns_gallery.expect(parser)
    def get(self, year=None):
        if year is not None:
            try:
                mainEvent = MainEvent.get(year=year)
            except MainEvent.DoesNotExist:
                return {'message': 'No such event'}, 404
            return paginate(mainEvent.albums, GalleryAlbumSchema())
        return paginate(
            GalleryAlbum.select().where(
                GalleryAlbum.mainEvent == None  # noqa: E711
            ),
            GalleryAlbumSchema(),
        )
