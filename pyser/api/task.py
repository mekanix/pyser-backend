from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restplus import Resource

from ..models.talk import Talk
from .namespaces import ns_talk
from .pagination import paginate, parser
from .schemas import TalkSchema


@ns_talk.route('', endpoint='talks')
@ns_talk.response(404, 'Talk not found')
class TalkListAPI(Resource):
    @ns_talk.expect(parser)
    def get(self):
        """Get list of talks"""
        return paginate(Talk.select(), TalkSchema())

    @jwt_required
    @ns_talk.expect(TalkSchema.fields())
    def post(self):
        schema = TalkSchema()
        talk, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 400
        talk.save()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        return response
