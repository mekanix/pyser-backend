from flask import current_app, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_mail import Message
from flask_smorest import Blueprint, abort
from peewee import fn

from freenit.schemas.paging import PageInSchema, paginate
from freenit.models.user import User

from ..models.cfs import CfS
from ..models.event import Event
from ..schemas.cfs import CfSPageOutSchema, CfSSchema

blueprint = Blueprint('cfs', 'cfs')


@blueprint.route('/<year>', endpoint='cfs_list')
class CfSAPI(MethodView):
    @blueprint.arguments(PageInSchema(), location='headers')
    @blueprint.response(CfSPageOutSchema)
    def get(self, pagination, year):
        """Get list of sponsors"""
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            abort(404, message='Event not found')
        return paginate(event.cfs, pagination)


@blueprint.route('', endpoint='cfs_create')
class CfSCreateAPI(MethodView):
    @blueprint.arguments(CfSSchema)
    @blueprint.response(CfSSchema)
    def post(self, args):
        """Create new CfS"""
        cfs = CfS(**args)
        year = Event.select(fn.Max(Event.year))
        event = Event.get(year=year)
        cfs.event = event
        cfs.save()
        msg = Message(
            '[PySer CfS] {}'.format(cfs.organization),
            sender=cfs.email,
            recipients=[current_app.config['MAIL_ADDRESS']],
        )
        referer = request.headers['Referer']
        msg.body = cfs.message
        msg.body += '\nCheck out {}/{}'.format(referer, cfs.id)
        current_app.mail.send(msg)
        return cfs


@blueprint.route('/detail/<cfs_id>', endpoint='cfs')
class CfSDetailAPI(MethodView):
    @blueprint.response(CfSSchema)
    def get(self, cfs_id):
        """Get cfs details"""
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            abort(404, message='CfS not found')
        return cfs

    @jwt_required
    @blueprint.arguments(CfSSchema(partial=True))
    @blueprint.response(CfSSchema)
    def patch(self, args, cfs_id):
        """Edit sponsor"""
        try:
            user = User.get(id=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            abort(404, message='No such sponsor')
        try:
            cfs_user = args.get('user', None)
            try:
                cfs.user = User.get(email=cfs_user.email)
            except User.DoesNotExist:
                abort(404, message='User not found')
        except User.DoesNotExist:
            cfs.user = user
        cfs.save()
        return cfs

    @jwt_required
    @blueprint.response(CfSSchema)
    def delete(self, cfs_id):
        """Delete sponsor"""
        try:
            User.get(id=get_jwt_identity())
        except User.DoesNotExist:
            abort(404, message='User not found')
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            abort(404, message='No such sponsor')
        cfs.delete_instance()
        return cfs
