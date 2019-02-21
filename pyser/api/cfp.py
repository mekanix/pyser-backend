from flask import current_app
from flask_restplus import Resource, abort
#  from ..utils import send_mail
from .namespaces import ns_cfp
from .schemas import CfPSchema, TalkSchema
from ..models.auth import User
from ..models.event import Event


message_format = """
First Name: {person.firstName}
Last Name: {person.lastName}
Email: {person.email}
Twitter: {person.twitter}
Facebook: {person.facebook}
Bio:
{person.bio}
Title: {talk.title}
Type: {talk.type}
Duration: {talk.duration}min
Description:
{talk.description}
"""


@ns_cfp.route('', endpoint='cfp')
class CfpAPI(Resource):
    @ns_cfp.response(409, 'Invalid data')
    def post(self):
        """Authenticates and generates a token."""
        schema = CfPSchema()
        cfp, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        text = message_format.format(talk=cfp.talk, person=cfp.person)
        username = current_app.config.get('MAIL_USER', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_HOST', None)
        #  error = send_mail(cfp.talk.title, text, username, password, host)
        #  if error:
            #  return {'message': 'Unable to send email'}, 409
        try:
            cfp.person = User.get(email=cfp.person.email)
        except User.DoesNotExist:
            cfp.person.save()
        cfp.talk.event = Event.select().order_by(Event.year)[0]
        cfp.talk.user = cfp.person
        cfp.talk.save()
        schema = TalkSchema()
        response, errors = schema.dump(cfp.talk)
        if errors:
            return errors, 409
        return response
