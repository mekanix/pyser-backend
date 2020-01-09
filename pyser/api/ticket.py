from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required
from flask_smorest import Blueprint, abort
from freenit.api.methodviews import ProtectedMethodView
from freenit.models.user import User
from freenit.schemas.paging import PageInSchema, paginate

from ..models.event import Event
from ..models.ticket import Ticket
from ..schemas.ticket import TicketPageOutSchema, TicketSchema

blueprint = Blueprint('tickets', 'tickets')


@blueprint.route('/<int:year>', endpoint='list')
class TicketListAPI(ProtectedMethodView):
    @jwt_optional
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(TicketPageOutSchema)
    def get(self, pagination, year):
        """List ticket posts"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='Event does not exist')
        return paginate(event.tickets, pagination)

    @jwt_required
    @blueprint.arguments(TicketSchema(exclude=['canceled']))
    @blueprint.response(TicketSchema)
    def post(self, args, year):
        """Create ticket post"""
        user_id = get_jwt_identity()
        try:
            visitor = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='Event does not exist')
        ticket = Ticket(event=event, visitor=visitor, **args)
        ticket.save()
        return ticket


@blueprint.route('/<int:year>/<identifier>', endpoint='detail')
class TicketAPI(ProtectedMethodView):
    @blueprint.response(TicketSchema)
    def get(self, year, identifier):
        """Get ticket details"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='Event does not exist')
        try:
            ticket = Ticket.get(event=event, identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        return ticket

    @jwt_required
    @blueprint.arguments(TicketSchema(partial=True))
    @blueprint.response(TicketSchema)
    def patch(self, args, year, identifier):
        """Edit ticket details"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='Event does not exist')
        try:
            ticket = Ticket.get(event=event, identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        for field in args:
            setattr(ticket, field, args[field])
        ticket.save()
        return ticket

    @jwt_required
    @blueprint.response(TicketSchema)
    def delete(self, year, identifier):
        """Delete ticket"""
        try:
            event = Event.get(year=year)
        except Event.DoesNotExist:
            abort(404, message='Event does not exist')
        try:
            ticket = Ticket.get(event=event, identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        ticket.canceled = True
        ticket.save()
        return ticket
