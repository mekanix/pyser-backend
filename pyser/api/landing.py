from flask import current_app
from flask_restplus import Resource

from ..utils import send_mail
from .namespaces import ns_landing
from .schemas import EmailSchema


@ns_landing.route('/form', endpoint='landing_form')
class LandingFormAPI(Resource):
    def post(self):
        schema = EmailSchema()
        payload = dict(current_app.api.payload)
        payload['to'] = ''
        email, errors = schema.load(payload)
        if errors:
            return errors, 409
        response, errors = schema.dump(email)
        if errors:
            return errors, 409
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        to = current_app.config.get('MAIL_ADDRESS', None)
        subject = f'[PySer] {email.subject}'
        try:
            send_mail(
                email.fromAddress,
                to,
                subject,
                email.message,
                username,
                password,
                host,
                port,
            )
        except Exception:
            pass
        return response
