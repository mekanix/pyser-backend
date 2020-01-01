from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from freenit.models.user import User
from freenit.schemas.paging import PageInSchema, paginate

from ..models.event import Event
from ..models.hall import Hall
from ..schemas.hall import HallPageOutSchema, HallSchema

blueprint = Blueprint('halls', 'halls')


@blueprint.route('/<year>', endpoint='list')
class HallListAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(HallPageOutSchema)
    def get(self, pagination, year):
        """Get list of halls"""
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        return paginate(event.halls, pagination)

    @jwt_required
    @blueprint.arguments(HallSchema)
    @blueprint.response(HallSchema)
    def post(self, args, year):
        """Create new hall"""
        try:
            user = User.get(id=get_jwt_identity())
            if not user.admin:
                abort(403, message='Permission denied')
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            abort(404, message='No such event')
        hall = Hall(**args)
        hall.event = event
        hall.save()
        return hall


@blueprint.route('/<hall_id>', endpoint='detail')
class HallDetailAPI(MethodView):
    @blueprint.response(HallSchema)
    def get(self, hall_id):
        """Get hall details"""
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            abort(404, message='No such hall')
        return hall

    @jwt_required
    @blueprint.arguments(HallSchema(partial=True))
    @blueprint.response(HallSchema)
    def patch(self, args, hall_id):
        """Edit hall"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            abort(404, message='No such hall')
        for field in args:
            setattr(hall, field, args[field])
        try:
            hall_user = hall.user
            try:
                hall.user = User.get(email=hall_user.email)
            except User.DoesNotExist:
                abort(404, message='User not found')
        except User.DoesNotExist:
            hall.user = user
        hall.save()
        return hall

    @jwt_required
    @blueprint.response(HallSchema)
    def delete(self, hall_id):
        """Delete hall"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            hall = Hall.get(id=hall_id)
        except Hall.DoesNotExist:
            abort(404, message='No such hall')
        hall.delete_instance()
        return hall
