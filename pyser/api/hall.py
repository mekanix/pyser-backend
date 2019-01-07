from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource

from ..models.auth import User
from ..models.event import Event
from ..models.hall import Hall
from .namespaces import ns_hall
from .pagination import paginate, parser
from .schemas import HallSchema


@ns_hall.route('/<year>', endpoint='halls')
class HallListAPI(Resource):
    @ns_hall.expect(parser)
    def get(self, year):
        """Get list of halls"""
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        return paginate(event.halls, HallSchema())

    @jwt_required
    @ns_hall.expect(HallSchema.fields())
    def post(self, year):
        """Create new hall"""
        try:
            user = User.get(email=get_jwt_identity())
            if not user.admin:
                return {'message': 'Permission denied'}, 403
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = HallSchema()
        hall, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        hall.event = event
        hall.save()
        response, errors = schema.dump(hall)
        if errors:
            return errors, 409
        return response


@ns_hall.route('/<hall_id>', endpoint='hall')
class HallDetailAPI(Resource):
    def get(self, hall_id):
        """Get hall details"""
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            return {'message': 'No such hall'}, 404
        schema = HallSchema()
        response, errors = schema.dump(hall)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_hall.expect(HallSchema.fields())
    def patch(self, hall_id):
        """Edit hall"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            return {'message': 'No such hall'}, 404
        schema = HallSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        hall.description = data.description or hall.description
        hall.end = data.end or hall.end
        hall.published = data.published or hall.published
        hall.start = data.start or hall.start
        hall.text = data.text or hall.text
        hall.title = data.title or hall.title
        try:
            hall_user = data.user
            try:
                hall.user = User.get(email=hall_user.email)
            except User.DoesNotExist:
                return {'message': 'User not found'}, 404
        except User.DoesNotExist:
            hall.user = user
        hall.save()
        response, errors = schema.dump(hall)
        if errors:
            return errors, 409
        return response

    @jwt_required
    def delete(self, hall_id):
        """Delete hall"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            return {'message': 'No such hall'}, 404
        schema = HallSchema()
        response, errors = schema.dump(hall)
        if errors:
            return errors, 409
        hall.delete_instance()
        return response
