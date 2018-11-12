from flask_jwt_extended import get_jwt_identity

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
