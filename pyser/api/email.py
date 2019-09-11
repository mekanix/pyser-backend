from flask import current_app
from flask_jwt_extended import get_jwt_identity
from flask_rest_api import Blueprint, abort

from ..models.auth import User
from ..models.email import Email
from ..models.event import Event
from ..models.talk import Talk
from ..schemas.email import EmailSchema
from .methodviews import ProtectedMethodView

blueprint = Blueprint('email', 'email')


@blueprint.route('', endpoint='email')
class EmailAPI(ProtectedMethodView):
    @blueprint.arguments(EmailSchema)
    @blueprint.response(EmailSchema)
    def post(self, args):
        """Send email"""
        email = get_jwt_identity()
        try:
            adminUser = User.get(email=email)
        except User.DoesNotExist:
            return {'message': 'No such user'}, 404
        if not adminUser.admin:
            abort(403, message='Only admins can send messages')
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        baseQuery = User.select()
        email = Email(**args)
        if email.to == 'all':
            query = baseQuery
        elif email.to == 'admins':
            query = baseQuery.where(User.admin)
        elif email.to == 'presenters':
            events = Event.select().order_by(Event.year.desc())
            if events.count() == 0:
                return {'message': 'At least one event should exist'}, 409
            query = [
                talk.user for talk in events[0].talks.where(Talk.published)
            ]
        elif email.to == 'volunteers':
            query = baseQuery.where(User.volunteer)
        else:
            return {'message': 'No such user group'}, 409
        if email.fromAddress == 'office':
            fromAddress = current_app.config.get('MAIL_ADDRESS', None)
        elif email.fromAddress == 'me':
            fromAddress = adminUser.email
        else:
            return {'message': 'Invalid "fromAddress" parameter'}, 409
        for user in query:
            try:
                send_mail(
                    fromAddress,
                    user.email,
                    email.subject,
                    email.message,
                    username,
                    password,
                    host,
                    port,
                )
            except Exception:
                pass
        return email
