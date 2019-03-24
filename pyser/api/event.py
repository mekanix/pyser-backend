from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restplus import Resource

from ..models.auth import User
from ..models.event import Event
from ..models.gallery import GalleryAlbum
from ..models.hall import Hall
from .namespaces import ns_event
from .pagination import paginate, parser
from .schemas import EventSchema


@ns_event.route('', endpoint='events')
class EventListAPI(Resource):
    @ns_event.expect(parser)
    def get(self):
        return paginate(Event.select(), EventSchema())

    @jwt_required
    @ns_event.expect(EventSchema.fields())
    def post(self):
        schema = EventSchema()
        event, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        try:
            Event.get(year=event.year)
            return {'message': 'Event in that year already exists'}, 409
        except Event.DoesNotExist:
            event.published = False
            event.save()
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        if not user.admin:
            return {'message': 'Admin area'}, 403
        gallery_album = GalleryAlbum(event=event, name='main')
        gallery_album.save()
        hall = Hall(event=event, name='main')
        hall.save()
        response, errors = schema.dump(event)
        if errors:
            return errors, 409
        return response


@ns_event.route('/<int:year>', endpoint='event')
class EventAPI(Resource):
    def get(self, year):
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = EventSchema()
        response, errors = schema.dump(event)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_event.expect(EventSchema.fields())
    def patch(self, year):
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = EventSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        event.year = data.year or event.year
        event.save()
        response, errors = schema.dump(event)
        if errors:
            return errors, 409
        return response

    @jwt_required
    def delete(self, year):
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = EventSchema()
        response, errors = schema.dump(event)
        if errors:
            return errors, 409
        event.delete_instance()
        return response
