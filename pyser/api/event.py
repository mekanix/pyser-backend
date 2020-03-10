from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required
from flask_smorest import Blueprint, abort
from freenit.models.user import User
from freenit.schemas.paging import PageInSchema, paginate

from ..models.event import Event
from ..models.gallery import GalleryAlbum
from ..models.hall import Hall
from ..schemas.event import EventPageOutSchema, EventSchema

blueprint = Blueprint('events', 'events')


@blueprint.route('', endpoint='list')
class EventListAPI(MethodView):
    @jwt_optional
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(EventPageOutSchema)
    def get(self, pagination):
        """List events"""
        identity = get_jwt_identity()
        query = Event.select().order_by(Event.year.desc())
        user = None
        if identity:
            try:
                user = User.get(id=identity)
            except User.DoesNotExist:
                abort(404, message='No such user')
        if not user or not user.admin:
            query = query.where(Event.published)
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
            user = User.get(id=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        if not user.admin:
            abort(403, message='Admin area')
        gallery_album = GalleryAlbum(event=event, name='main')
        gallery_album.save()
        hall = Hall(event=event, name='main')
        hall.save()
        return event


@blueprint.route('/<int:year>', endpoint='detail')
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
