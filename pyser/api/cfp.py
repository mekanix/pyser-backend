from flask import current_app, request
from flask.views import MethodView
from flask_rest_api import Blueprint

from ..models.auth import User
from ..models.cfp import CfP
from ..models.event import Event
#  from ..utils import send_mail
from ..schemas.cfp import CfPSchema

message_format = """
Details: {referrer}/{talk.id}

First Name: {person.firstName}
Last Name: {person.lastName}
Email: {person.email}
Twitter: {person.twitter}
Facebook: {person.facebook}
Bio:
{person.bio}


Title: {talk.title}
Hall: {talk.hall}
Duration: {talk.duration}min
Description:
{talk.description}
"""

presenter_message_format = """
Thank you for applying to Python Serbia conference! Your paper titled

{}

is in review.
"""

subject_format = "[CfP] {}"
blueprint = Blueprint('cfp', 'cfp')


@blueprint.route('', endpoint='cfp')
class CfpAPI(MethodView):
    @blueprint.arguments(CfPSchema)
    @blueprint.response(CfPSchema)
    def post(self, args):
        """Submit talk proposal"""
        cfp = CfP(**args)
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        to = current_app.config.get('MAIL_ADDRESS', None)
        subject = subject_format.format(cfp.talk.title)
        fromAddress = cfp.person.email
        try:
            cfp.person = User.get(email=cfp.person.email)
        except User.DoesNotExist:
            cfp.person.active = True
            cfp.person.admin = False
            cfp.person.volunteer = False
            cfp.person.save()
        events = Event.select().order_by(Event.year.desc())
        cfp.talk.event = events[0]
        cfp.talk.user = cfp.person
        cfp.talk.save()
        text = message_format.format(
            talk=cfp.talk,
            person=cfp.person,
            referrer=request.referrer,
        )
        #  error = send_mail(
        #  fromAddress,
        #  to,
        #  subject,
        #  text,
        #  username,
        #  password,
        #  host,
        #  port,
        #  )
        #  if error:
        #  return {'message': 'Unable to send email'}, 409
        text = presenter_message_format.format(cfp.talk.title)
        #  error = send_mail(
        #  to,
        #  fromAddress,
        #  subject,
        #  text,
        #  username,
        #  password,
        #  host,
        #  port,
        #  )
        #  if error:
        #  return {'message': 'Unable to send email'}, 409
        return cfp
