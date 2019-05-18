from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource
from urllib.parse import urlparse, parse_qs

from ..models.auth import User
from ..models.event import Event
from ..models.talk import Talk
from ..utils import send_mail
from .namespaces import ns_talk
from .pagination import paginate, parser
from .schemas import TalkSchema
from .resources import ProtectedResource

announce_subject = '[PySer] Your talk is {}accepted'
announce_message = """
Congratulation,

Your talk titled

"{}"

is accepted. See you at the conference!

Please review the schedule and contact us in the next 3 days if you can't
present at {}.

Regards,
PySer conference
"""

reject_message = """
Hello,

We're sorry to inform you that your talk

"{}"

is not accepted. We wish you more luck next time!

Regards,
PySer conference
"""


@ns_talk.route('/year/<year_id>', endpoint='talks')
class TalkListAPI(Resource):
    @ns_talk.expect(parser)
    def get(self, year_id):
        """Get list of talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = TalkSchema()
        data, errors = schema.dump(event.talks.order_by(Talk.start), many=True)
        if errors:
            return errors, 409
        return {
            'data': data,
            'pages': 1,
            'total': event.talks.count(),
        }

    @jwt_required
    @ns_talk.expect(TalkSchema.fields())
    def post(self, year_id):
        """Create new talk"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        schema = TalkSchema()
        talk, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
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
        talk.save()
        response, errors = schema.dump(talk)
        if errors:
            return errors, 409
        return response


@ns_talk.route('/year/<year_id>/user', endpoint='talks_user')
class UserTalkListAPI(ProtectedResource):
    @ns_talk.expect(parser)
    def get(self, year_id):
        """Get list of talks by user"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        allTalks = event.talks.join(User).where(Talk.user == user)
        query = allTalks.order_by(Talk.start)
        return paginate(query, TalkSchema())


@ns_talk.route('/year/<year_id>/published', endpoint='talks_published')
class PublishedTalkListAPI(Resource):
    @ns_talk.expect(parser)
    def get(self, year_id):
        """Get list of talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        query = event.talks.where(Talk.published).order_by(Talk.start)
        schema = TalkSchema()
        data, errors = schema.dump(query, many=True)
        if errors:
            return errors, 409
        return {
            'data': data,
            'pages': 1,
            'total': event.talks.count(),
        }


@ns_talk.route('/year/<year_id>/announce', endpoint='talks_announce')
class AnnounceTalkListAPI(ProtectedResource):
    def post(self, year_id):
        """Announce the talks"""
        try:
            event = Event.get(year=int(year_id))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        username = current_app.config.get('MAIL_USERNAME', None)
        password = current_app.config.get('MAIL_PASSWORD', None)
        host = current_app.config.get('MAIL_SERVER', None)
        port = current_app.config.get('MAIL_PORT', 25)
        for talk in event.talks.where(Talk.published):
            text = announce_message.format(talk.title, talk.start)
            subject = announce_subject.format('')
            try:
                error = send_mail(
                    'office@pyser.org',
                    talk.user.email,
                    subject,
                    text,
                    username,
                    password,
                    host,
                    port,
                )
            except Exception:
                pass
        for talk in event.talks.where(Talk.published == False):
            text = reject_message.format(talk.title)
            subject = announce_subject.format('not ')
            try:
                error = send_mail(
                    'office@pyser.org',
                    talk.user.email,
                    subject,
                    text,
                    username,
                    password,
                    host,
                    port,
                )
            except Exception:
                pass
        return {'message': 'OK'}


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
            User.get(email=get_jwt_identity())
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
        published = getattr(data, 'published', None)
        if published is not None:
            talk.published = data.published
        talk.start = data.start or talk.start
        talk.title = data.title or talk.title
        talk.hall = data.hall or talk.hall
        video = getattr(data, 'video', None)
        if video is not None:
            url = urlparse(video)
            args = parse_qs(url.query)
            video_id = args.get('v', None)
            if video_id is None:
                return {'message': 'Wrong URL'}, 409
            talk.video = video_id[0]
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
