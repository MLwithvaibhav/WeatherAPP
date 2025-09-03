from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'

db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()

# Marsahalling fields

weather_fields = {
    id: fields.Integer,
    'city': fields.String,
    'temperature': fields.Float,
    'description': fields.String,
    'humidity': fields.Integer,
    'wind_speed': fields.Float,
    'precipitation' : fields.Float,
    'pressure' : fields.Float,
    'feel_like' : fields.Float,
    'visibility' : fields.Integer,
    'timestamp' : fields.DateTime
}


