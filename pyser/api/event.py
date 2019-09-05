from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_rest_api import Blueprint, abort

from ..models.auth import User
from ..models.event import Event
from ..models.gallery import GalleryAlbum
from ..models.hall import Hall
from ..schemas.event import EventSchema
from ..schemas.paging import PageInSchema, PageOutSchema, paginate

blueprint = Blueprint('event', 'event')


@blueprint.route('', endpoint='events')
class EventListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(EventSchema))
    def get(self, pagination):
        """List events"""
        query = Event.select().order_by(Event.year.desc())
        return paginate(query, pagination)

    @jwt_required
    @blueprint.arguments(EventSchema)
    @blueprint.response(EventSchema)
    def post(self, args):
        """Create event"""
        event = Event(**args)
        try:
            Event.get(year=event.year)
            abort(409, message='Event in that year already exists')
        except Event.DoesNotExist:
            event.published = False
            event.save()
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        if not user.admin:
            abort(403, message='Admin area')
        gallery_album = GalleryAlbum(event=event, name='main')
        gallery_album.save()
        hall = Hall(event=event, name='main')
        hall.save()
        return event


@blueprint.route('/<int:year>', endpoint='event')
class EventAPI(MethodView):
    @blueprint.response(EventSchema)
    def get(self, year):
        """Get event details"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='No such event')
        return event

    @jwt_required
    @blueprint.arguments(EventSchema(partial=True))
    @blueprint.response(EventSchema)
    def patch(self, args, year):
        """Edit event details"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='No such event')
        for field in args:
            setattr(event, field, args[field])
        event.save()
        return event

    @jwt_required
    @blueprint.response(EventSchema)
    def delete(self, year):
        """Delete event"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='No such event')
        event.delete_instance()
        return event
