from email.mime.text import MIMEText

from flask import current_app
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint, abort
from freenit.api.methodviews import ProtectedMethodView
from freenit.models.user import User

from ..models.email import Email
from ..models.event import Event
from ..models.talk import Talk
from ..schemas.email import EmailSchema

blueprint = Blueprint('email', 'email')


@blueprint.route('', endpoint='email')
class EmailAPI(ProtectedMethodView):
    @blueprint.arguments(EmailSchema)
    @blueprint.response(EmailSchema)
    def post(self, args):
        """Send email"""
        user_id = get_jwt_identity()
        try:
            adminUser = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='No such user')
        if not adminUser.admin:
            abort(403, message='Only admins can send messages')
        baseQuery = User.select()
        email = Email(**args)
        msg = MIMEText(email.message, 'plain', 'utf-8')
        if email.to == 'all':
            query = baseQuery
        elif email.to == 'admins':
            query = baseQuery.where(User.admin)
        elif email.to == 'presenters':
            events = Event.select().order_by(Event.year.desc())
            if events.count() == 0:
                abort(409, message='At least one event should exist')
            query = [
                talk.user for talk in events[0].talks.where(Talk.published)
            ]
        elif email.to == 'volunteers':
            query = baseQuery.where(User.volunteer)
        else:
            abort(409, message='No such user group')
        if email.fromAddress == 'office':
            msg['From'] = current_app.config.get('FROM_EMAIL', None)
        elif email.fromAddress == 'me':
            msg['From'] = adminUser.email
        else:
            abort(409, message='Invalid "fromAddress" parameter')
        msg['Subject'] = email.subject
        msg['To'] = [user.email for user in query]
        try:
            current_app.sendmail(msg)
        except Exception:
            pass
        return email
