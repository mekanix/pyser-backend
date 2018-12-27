from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restplus import Resource

from ..models.event import MainEvent
from .namespaces import ns_main
from .pagination import paginate, parser
from .schemas import MainEventSchema


@ns_main.route('', endpoint='mains')
class MainEventListAPI(Resource):
    @ns_main.expect(parser)
    def get(self):
        return paginate(MainEvent.select(), MainEventSchema())

    @jwt_required
    @ns_main.expect(MainEventSchema.fields())
    def post(self):
        schema = MainEventSchema()
        event, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        try:
            MainEvent.get(year=event.year)
            return {'message': 'Main event in that year already exists'}, 409
        except MainEvent.DoesNotExist:
            event.save()
        return schema.dump(event)


@ns_main.route('/<int:year>', endpoint='main')
class MainEventAPI(Resource):
    def get(self, year):
        try:
            mainEvent = MainEvent.get(year=year)
        except MainEvent.DoesNotExist:
            return {'message': 'No such main event'}, 404
        schema = MainEventSchema()
        response, errors = schema.dump(mainEvent)
        if errors:
            return errors, 409
        return response

    @jwt_required
    @ns_main.expect(MainEventSchema.fields())
    def patch(self, year):
        try:
            mainEvent = MainEvent.get(year=year)
        except MainEvent.DoesNotExist:
            return {'message': 'No such main event'}, 404
        schema = MainEventSchema()
        data, errors = schema.load(current_app.api.payload)
        if errors:
            return errors, 409
        mainEvent.year = data.year or mainEvent.year
        mainEvent.save()
        response, errors = schema.dump(mainEvent)
        if errors:
            return errors, 409
        return response

    @jwt_required
    def delete(self, year):
        try:
            mainEvent = MainEvent.get(year=year)
        except MainEvent.DoesNotExist:
            return {'message': 'No such main event'}, 404
        schema = MainEventSchema()
        response, errors = schema.dump(mainEvent)
        if errors:
            return errors, 409
        mainEvent.delete_instance()
        return response
