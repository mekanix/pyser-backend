from string import ascii_letters
from random import choice
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource
from flask_security.utils import hash_password

from flask import current_app

from ..models.auth import User
from ..utils import send_mail
from .namespaces import ns_user
from .pagination import paginate, parser
from .resources import ProtectedResource
from .schemas import UserSchema, VolunteerCountSchema

message_format = """
Thank you for applying as volunteer for Python Serbia conference!
"""


@ns_user.route('', endpoint='users')
class UserListAPI(ProtectedResource):
    @ns_user.expect(parser)
    def get(self):
        """List users"""
        return paginate(User.select().order_by(User.id), UserSchema())

    @ns_user.expect(UserSchema.fields())
    def post(self):
        """Create user"""
        schema = UserSchema()
        user, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        user.password = hash_password(user.password)
        user.save()
        return schema.dump(user)


@ns_user.route('/<user_id>', endpoint='user')
@ns_user.response(404, 'User not found')
class UserAPI(Resource):
    def get(self, user_id):
        """Get user details"""
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        schema = UserSchema()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_user.expect(UserSchema.fields())
    def patch(self, user_id):
        """Edit user"""
        try:
            admin_user = User.get(email=get_jwt_identity())
            if not admin_user.admin:
                return {'message': 'Not an admin user'}, 403
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            return {'message': 'No such talk'}, 404
        schema = UserSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        active = getattr(data, 'active', None)
        if active is not None:
            user.active = active
        admin = getattr(data, 'admin', None)
        if admin is not None:
            user.admin = admin
        user.save()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response


@ns_user.route('/volunteering', endpoint='volunteering')
class VolunteeringUserAPI(Resource):
    @jwt_required
    @ns_user.expect(parser)
    def get(self):
        """List volunteers"""
        try:
            admin_user = User.get(email=get_jwt_identity())
            if not admin_user.admin:
                return {'message': 'Not an admin user'}, 403
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        return paginate(
            User.select().where(User.volunteer).order_by(User.id),
            UserSchema(),
        )

    @ns_user.expect(UserSchema.fields())
    def post(self):
        """Create new volunteer"""
        schema = UserSchema()
        data, errors = schema.load(current_app.api.payload)
        volunteers = User.select().where(User.volunteer)
        volunteerCount = volunteers.count()
        print(volunteerCount, volunteerCount >= 10)
        if errors:
            return errors, 409
        try:
            user = User.get(email=data.email)
        except User.DoesNotExist:
            user = data
            plaintext = ''.join(choice(ascii_letters) for _ in range(16))
            user.password = hash_password(plaintext)
        user.volunteer = True
        user.save()
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        fromAddress = current_app.config.get('MAIL_ADDRESS', None)
        subject = '[PySer] Volunteering'
        text = message_format.format()
        error = send_mail(
            fromAddress,
            user.email,
            subject,
            text,
            username,
            password,
            host,
            port,
        )
        if error:
            return {'message': 'Unable to send email'}, 409
        subject = '[Volunteering]'
        text = '{} applied as volunteer'.format(user.email)
        error = send_mail(
            user.email,
            fromAddress,
            subject,
            text,
            username,
            password,
            host,
            port,
        )
        if error:
            return {'message': 'Unable to send email'}, 409
        return schema.dump(user)


@ns_user.route('/volunteering/count', endpoint='volunteering_count')
class VolunteerCountAPI(Resource):
    def get(self):
        """Get volunteer count"""
        volunteers = User.select().where(User.volunteer)
        volunteerCount = volunteers.count()
        volunteerMax = current_app.config.get('VOLUNTEER_COUNT', 15)
        schema = VolunteerCountSchema()
        response, errors = schema.dump({
            'count': volunteerCount,
            'max': volunteerMax,
        })
        if errors:
            return errors, 409
        return response
