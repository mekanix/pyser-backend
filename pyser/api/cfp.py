from email.mime.text import MIMEText

from flask import current_app
from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint, abort
from freenit.api.methodviews import ProtectedMethodView
from freenit.models.user import User

from ..models.cfp import CfP
from ..models.event import Event
from ..models.talk import Talk
from ..schemas.cfp import CfPSchema
from ..schemas.talk import TalkSchema

presenter_message_format = """
Thank you for applying to Python Serbia conference! Your paper titled

{}

is in review.
"""

subject_format = "[CfP] {}"
blueprint = Blueprint('cfp', 'cfp')


@blueprint.route('', endpoint='cfp')
class CfpAPI(ProtectedMethodView):
    @blueprint.arguments(TalkSchema)
    @blueprint.response(CfPSchema)
    def post(self, args):
        """Submit talk proposal"""
        talk = Talk(**args)
        talk.published = False
        user_id = get_jwt_identity()
        try:
            person = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='No such user')
        cfp = CfP(person, talk)
        events = Event.select().order_by(Event.year.desc())
        cfp.talk.event = events[0]
        cfp.talk.user = cfp.person
        cfp.talk.save()
        message = presenter_message_format.format(cfp.talk.title)
        config = current_app.config
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = current_app.config.get('FROM_EMAIL', None)
        msg['Subject'] = config['SUBJECTS']['prefix'] + 'Paper submission'
        msg['To'] = person.email
        msg['Bcc'] = msg['From']
        current_app.sendmail(msg)
        return cfp
