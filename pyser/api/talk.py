from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource

from ..models.auth import User
from ..models.event import Event
from ..models.talk import Talk
from .namespaces import ns_talk
from .pagination import paginate, parser
from .schemas import TalkSchema


@ns_talk.route('/<year>', endpoint='talks')
class TalkListAPI(Resource):
    @ns_talk.expect(parser)
    def get(self, year):
        """Get list of talks"""
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        return paginate(event.talks, TalkSchema())

    @jwt_required
    @ns_talk.expect(TalkSchema.fields())
    def post(self, year):
        """Create new talk"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = TalkSchema()
        talk, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 400
        if not user.admin:
            talk.user = user
        else:
            try:
                talk_user = talk.user
                try:
                    talk.user = User.get(email=talk_user.email)
                except User.DoesNotExist:
                    return {'message': 'User not found'}, 404
            except User.DoesNotExist:
                talk.user = user
        talk.event = event
        print(talk.event)
        talk.save()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        return response


@ns_talk.route('/<talk_id>', endpoint='talk')
class TalkDetailAPI(Resource):
    def get(self, talk_id):
        """Get talk details"""
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            return {'message': 'No such talk'}, 404
        schema = TalkSchema()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_talk.expect(TalkSchema.fields())
    def patch(self, talk_id):
        """Edit talk"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            return {'message': 'No such talk'}, 404
        schema = TalkSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        talk.description = data.description or talk.description
        talk.end = data.end or talk.end
        talk.published = data.published or talk.published
        talk.start = data.start or talk.start
        talk.text = data.text or talk.text
        talk.title = data.title or talk.title
        try:
            talk_user = data.user
            try:
                talk.user = User.get(email=talk_user.email)
            except User.DoesNotExist:
                return {'message': 'User not found'}, 404
        except User.DoesNotExist:
            talk.user = user
        talk.save()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        return response

    @jwt_required
    def delete(self, talk_id):
        """Delete talk"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            talk = Talk.get(id=talk_id)
        except Talk.DoesNotExist:
            return {'message': 'No such talk'}, 404
        schema = TalkSchema()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        talk.delete_instance()
        return response
