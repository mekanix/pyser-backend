from random import choice
from string import ascii_letters

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_rest_api import Blueprint, abort
from flask_security.utils import hash_password

from ..models.auth import User
from ..schemas.auth import UserSchema
from ..schemas.paging import PageInSchema, PageOutSchema, paginate
from ..utils import send_mail
from .methodviews import ProtectedMethodView

blueprint = Blueprint('user', 'user')
message_format = """
Thank you for applying as volunteer for Python Serbia conference!
"""


@blueprint.route('', endpoint='users')
class UserListAPI(ProtectedMethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(UserSchema))
    def get(self, pagination):
        """List users"""
        return paginate(User.select(), pagination)

    @blueprint.arguments(UserSchema)
    @blueprint.response(UserSchema)
    def post(self, args):
        """Create user"""
        user = User(**args)
        if user.password:
            user.password = hash_password(user.password)
        user.save()
        return user


@blueprint.route('/volunteering', endpoint='volunteering')
class VolunteeringUserAPI(MethodView):
    @jwt_required
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(PageOutSchema(UserSchema))
    def get(self, pagination):
        """List volunteers"""
        try:
            admin_user = User.get(email=get_jwt_identity())
            if not admin_user.admin:
                return {'message': 'Not an admin user'}, 403
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        return paginate(
            User.select().where(User.volunteer).order_by(User.id),
            pagination,
        )

    @blueprint.arguments(UserSchema)
    @blueprint.response(UserSchema)
    def post(self, args):
        """Create new volunteer"""
        #  volunteers = User.select().where(User.volunteer)
        #  volunteerCount = volunteers.count()
        try:
            user = User.get(email=args['email'])
        except User.DoesNotExist:
            user = User(**args)
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
            abort(409, message='Unable to send email')
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
            abort(409, message='Unable to send email')
        return user


@blueprint.route('/<user_id>', endpoint='user')
class UserAPI(ProtectedMethodView):
    @blueprint.response(UserSchema)
    def get(self, user_id):
        """Get user details"""
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        return user

    @blueprint.arguments(UserSchema(partial=True))
    @blueprint.response(UserSchema)
    def patch(self, args, user_id):
        """Edit user details"""
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        for field in args:
            setattr(user, field, args[field])
        if 'password' in args:
            user.password = hash_password(user.password)
        user.save()
        return user

    @blueprint.response(UserSchema)
    def delete(self, user_id):
        """Delete user"""
        try:
            user = User.get(id=user_id)
        except User.DoesNotExist:
            abort(404, message='User not found')
        user.delete_instance()
        return user
