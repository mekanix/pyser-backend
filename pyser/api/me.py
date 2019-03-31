from flask import current_app
from flask_jwt_extended import get_jwt_identity
from flask_security.utils import hash_password

from ..models.auth import User
from .namespaces import ns_me
from .resources import ProtectedResource
from .schemas import UserSchema


@ns_me.route('', endpoint='me')
@ns_me.response(404, 'User not found')
class MeAPI(ProtectedResource):
    def get(self):
        """Get my details"""
        email = get_jwt_identity()
        try:
            user = User.get(email=email)
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        schema = UserSchema()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response

    @ns_me.expect(UserSchema.fields(required=False))
    def patch(self):
        """Edit my details"""
        email = get_jwt_identity()
        try:
            user = User.get(email=email)
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        schema = UserSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        user.firstName = data.firstName or user.firstName
        user.lastName = data.lastName or user.lastName
        user.email = data.email or user.email
        user.bio = data.bio or user.bio
        user.twitter = data.twitter or user.twitter
        user.facebook = data.facebook or user.facebook
        if data.password:
            user.password = hash_password(user.password)
        user.save()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response
