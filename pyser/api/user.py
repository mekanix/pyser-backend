from flask import current_app

from ..models.auth import User
from .namespaces import ns_user
from .resources import ProtectedResource
from .schemas import UserSchema


@ns_user.route('', endpoint='users')
class UserListAPI(ProtectedResource):
    def get(self):
        """List users"""
        schema = UserSchema(many=True)
        response, errors = schema.dump(User.select())
        if errors:
            return errors, 409
        return response

    @ns_user.expect(UserSchema.fields())
    def post(self):
        schema = UserSchema()
        user, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        user.save()
        return schema.dump(user)


@ns_user.route('/<id>', endpoint='user')
@ns_user.response(404, 'User not found')
class UserAPI(ProtectedResource):
    def get(self, id):
        """Get user details"""
        try:
            user = User.get(id=id)
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        schema = UserSchema()
        response, errors = schema.dump(user)
        if errors:
            return errors, 409
        return response
