from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource
from flask_security.utils import hash_password

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
        return paginate(User.select(), UserSchema())

    @ns_user.expect(UserSchema.fields())
    def post(self):
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
        user.save()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response
