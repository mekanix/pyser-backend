#  from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint

from ..models.email import Email
from ..schemas.email import EmailSchema

blueprint = Blueprint('landing', 'landing')


@blueprint.route('/form', endpoint='landing_form')
class LandingFormAPI(MethodView):
    @blueprint.arguments(EmailSchema)
    @blueprint.response(EmailSchema)
    def post(self, args):
        """Send email"""
        args['to'] = ''
        email = Email(**args)
        #  username = current_app.config.get('MAIL_USERNAME', None)
        #  password = current_app.config.get('MAIL_PASSWORD', None)
        #  host = current_app.config.get('MAIL_SERVER', None)
        #  port = current_app.config.get('MAIL_PORT', 25)
        #  to = current_app.config.get('MAIL_ADDRESS', None)
        #  subject = f'[PySer] {email.subject}'
        #  try:
        #  send_mail(
        #  email.fromAddress,
        #  to,
        #  subject,
        #  email.message,
        #  username,
        #  password,
        #  host,
        #  port,
        #  )
        #  except Exception:
        #  pass
        return email
