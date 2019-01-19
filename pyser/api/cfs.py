from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_mail import Message
from flask_restplus import Resource
from peewee import fn

from ..models.auth import User
from ..models.cfs import CfS
from ..models.event import Event
from .namespaces import ns_cfs
from .pagination import paginate, parser
from .schemas import CfSSchema


@ns_cfs.route('/<year>', endpoint='cfs_list')
class cfsAPI(Resource):
    @ns_cfs.expect(parser)
    def get(self, year):
        """Get list of sponsors"""
        try:
            event = Event.get(year=int(year))
        except Event.DoesNotExist:
            return {'message': 'No such event'}, 404
        return paginate(event.cfs, CfSSchema())


@ns_cfs.route('', endpoint='cfs_create')
class CfSCreateAPI(Resource):
    @ns_cfs.expect(CfSSchema.fields())
    def post(self):
        """Create new CfS"""
        schema = CfSSchema()
        cfs, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        year = Event.select(fn.Max(Event.year))
        event = Event.get(year=year)
        cfs.event = event
        cfs.save()
        response, errors = schema.dump(cfs)
        if errors:
            return errors, 409
        msg = Message(
            '[PySer CfS] {}'.format(cfs.organization),
            sender=cfs.email,
            recipients=[current_app.config['MAIL_ADDRESS']],
        )
        referer = request.headers['Referer']
        msg.body = cfs.message
        msg.body += '\nCheck out {}/{}'.format(referer, cfs.id)
        current_app.mail.send(msg)
        return response


@ns_cfs.route('/<cfs_id>', endpoint='cfs')
class CfSDetailAPI(Resource):
    def get(self, cfs_id):
        """Get cfs details"""
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            return {'message': 'No such sponsor'}, 404
        schema = CfSSchema()
        response, errors = schema.dump(cfs)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_cfs.expect(CfSSchema.fields())
    def patch(self, cfs_id):
        """Edit sponsor"""
        try:
            user = User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            return {'message': 'No such sponsor'}, 404
        schema = CfSSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        try:
            cfs_user = data.user
            try:
                cfs.user = User.get(email=cfs_user.email)
            except User.DoesNotExist:
                return {'message': 'User not found'}, 404
        except User.DoesNotExist:
            cfs.user = user
        cfs.save()
        response, errors = schema.dump(cfs)
        if errors:
            return errors, 409
        return response

    @jwt_required
    def delete(self, cfs_id):
        """Delete sponsor"""
        try:
            User.get(email=get_jwt_identity())
        except User.DoesNotExist:
            return {'message': 'User not found'}, 404
        try:
            cfs = CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            return {'message': 'No such sponsor'}, 404
        schema = CfSSchema()
        response, errors = schema.dump(cfs)
        if errors:
            return errors, 409
        cfs.delete_instance()
        return response
