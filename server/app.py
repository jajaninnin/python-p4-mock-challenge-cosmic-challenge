#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from sqlalchemy.exc import NoResultFound
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)

migrate = Migrate(app, db)

db.init_app(app)

# @app.route('/')
# def home():
#     return ''

class Scientists(Resource):
    def get(self):
        scientists = db.session.execute(db.select(Scientist)).scalars()
        list_scientists = [sci.to_dict(rules=('-missions',)) for sci in scientists]
        return make_response(list_scientists)

    def post(self):
        data = request.json
        try:
            new_scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except:
            response_body = {'errors': ['validation errors']}
            return make_response(response_body, 400)

class ScientistById(Resource):
    def get(self, id):
        try:
            scientist = db.session.execute(db.select(Scientist).filter_by(id=id)).scalar_one()
            return make_response(scientist.to_dict())
        except:
            return make_response({'error': 'Scientist not found'}, 404)

    def patch(self, id):
        try:
            scientist = db.session.execute(db.select(Scientist).filter_by(id=id)).scalar_one()
            params = request.json
            for attr in params:
                setattr(scientist, attr, params[attr])
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        except NoResultFound:
            return make_response({'error': 'Scientist not found'}, 404)
        except:
            response_body = {'errors': ['validation errors']}
            return make_response(response_body, 400)

    def delete(self, id):
        try:
            scientist = db.session.execute(db.select(Scientist).filter_by(id=id)).scalar_one()
            db.session.delete(scientist)
            db.session.commit()
            return make_response(jsonify(""), 204)
        except:
            response_body = {'error': 'Scientist not found'}
            return make_response(response_body, 404)

class Planets(Resource):
    def get(self):
        planets = db.session.execute(db.select(Planet)).scalars()
        list_planets = [plan.to_dict() for plan in planets]
        return make_response(list_planets)

class Missions(Resource):
    def post(self):
        try:
            data = request.json
            new_mission = Mission(
                name=data['name'], 
                scientist_id=data['scientist_id'], 
                planet_id=data['planet_id']
                )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except:
            return make_response({'errors': ['validation errors']}, 400)
        
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Scientists, '/scientists')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
