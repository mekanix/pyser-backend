from string import ascii_letters
from random import choice
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource
from flask_security.utils import hash_password

from flask import current_app

from ..models.auth import User
from .namespaces import ns_user
from .pagination import paginate, parser
from .resources import ProtectedResource
from .schemas import UserSchema


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
    @ns_user.expect(parser)
    def get(self):
        """List volunteers"""
        return paginate(
            User.select().where(User.volunteer).order_by(User.id),
            UserSchema(),
        )

    @ns_user.expect(UserSchema.fields())
    def post(self):
        """Create new volunteer"""
        schema = UserSchema()
        user, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        user.volunteer = True
        plaintext = ''.join(choice(ascii_letters) for _ in range(16))
        user.password = hash_password(plaintext)
        user.save()
        return schema.dump(user)
