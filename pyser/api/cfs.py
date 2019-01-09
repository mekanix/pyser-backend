from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restplus import Resource

from ..models.auth import User
from ..models.event import Event
from ..models.cfs import CfS
from .namespaces import ns_cfs
from .pagination import paginate, parser
from .schemas import CfSSchema
from peewee import fn


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
        return response

@ns_cfs.route('/<hall_id>', endpoint='cfs')
class CfSDetailAPI(Resource):
    def get(self, cfs_id):
        """Get cfs details"""
        try:
            cfs = CfS.get(id=hall_id)
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
            cfs= CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            return {'message': 'No such sponsor'}, 404
        schema = CfSSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        #  cfs.description = data.description or cfs.description
        #  cfs.end = data.end or cfs.end
        #  cfs.published = data.published or cfs.published
        #  cfs.start = data.start or cfs.start
        #  cfs.text = data.text or cfs.text
        #  cfs.title = data.title or cfs.title
        try:
            cfs_user= data.user
            try:
                cfs.user = User.get(email=cfs_user.email)
            except User.DoesNotExist:
                return {'message': 'User not found'}, 404
        except User.DoesNotExist:
            cfs.user = user
        cfs.save()
        response, errors = schema.dump(hall)
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
            cfs= CfS.get(id=cfs_id)
        except CfS.DoesNotExist:
            return {'message': 'No such sponsor'}, 404
        schema = CfSSchema()
        response, errors = schema.dump(cfs)
        if errors:
            return errors, 409
        cfs.delete_instance()
        return response
