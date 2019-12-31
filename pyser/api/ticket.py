from flask_jwt_extended import get_jwt_identity, jwt_optional, jwt_required
from flask_smorest import Blueprint, abort
from freenit.api.methodviews import MethodView
from freenit.models.user import User
from freenit.schemas.paging import PageInSchema, paginate

from ..models.ticket import Ticket
from ..schemas.ticket import TicketPageOutSchema, TicketSchema

blueprint = Blueprint('tickets', 'tickets')


@blueprint.route('', endpoint='list')
class TicketListAPI(MethodView):
    @jwt_optional
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(TicketPageOutSchema)
    def get(self, pagination):
        """List ticket posts"""
        return paginate(Ticket.select(), pagination)

    @jwt_required
    @blueprint.arguments(TicketSchema)
    @blueprint.response(TicketSchema)
    def post(self, args):
        """Create ticket post"""
        user_id = get_jwt_identity()
        try:
            visitor = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        ticket = Ticket(**args)
        ticket.visitor = visitor
        ticket.save()
        return ticket


@blueprint.route('/<identifier>', endpoint='detail')
class TicketAPI(MethodView):
    @blueprint.response(TicketSchema)
    def get(self, identifier):
        """Get ticket details"""
        try:
            ticket = Ticket.get(identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        return ticket

    @jwt_required
    @blueprint.arguments(TicketSchema(partial=True))
    @blueprint.response(TicketSchema)
    def patch(self, args, identifier):
        """Edit ticket details"""
        try:
            ticket = Ticket.get(identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        for field in args:
            setattr(ticket, field, args[field])
        ticket.save()
        return ticket

    @jwt_required
    @blueprint.response(TicketSchema)
    def delete(self, identifier):
        """Delete ticket"""
        try:
            ticket = Ticket.get(identifier=identifier)
        except Ticket.DoesNotExist:
            abort(404, message='No such ticket')
        ticket.canceled = True
        ticket.save()
        return ticket
