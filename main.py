from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import request
from datetime import datetime

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()
API_KEY = "YOUR_OPENWEATHER_API_KEY" 

class WeatherModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Marsahalling fields

weather_fields = {
    "id": fields.Integer,
    'city': fields.String,
    'temperature': fields.Float,
    'description': fields.String,
    'humidity': fields.Integer,
    'wind_speed': fields.Float,
    'pressure' : fields.Float,
    'feel_like' : fields.Float,
    'timestamp' : fields.DateTime
}
# request parser
parsers= reqparse.RequestParser()
parsers.add_argument('city', type=str, help='City name is required', required=True)

class Weather(Resource):
    @marshal_with(weather_fields)
    def get(self):
        args = parsers.parse_args()
        city = args["city"]

        # OpenWeather API call
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = request.get(url).json()

        # Agar city galat hai toh error handle karna
        if response.get("cod") != 200:
            return {"message": "City not found"}, 404

        # Data nikalna
        data = WeatherModel(
            city=response["name"],
            temperature=response["main"]["temp"],
            description=response["weather"][0]["description"],
            humidity=response["main"]["humidity"],
            wind_speed=response["wind"]["speed"],
            pressure=response["main"]["pressure"],
            feels_like=response["main"]["feels_like"]
        )

        # DB me save karna
        db.session.add(data)
        db.session.commit()

        return data, 200
    

class History(Resource):
    @marshal_with(weather_fields)
    def get(self):
        records = WeatherModel.query.all()
        return records, 200


# ------------------------------
# Routes
# ------------------------------
api.add_resource(Weather, "/weather")
api.add_resource(History, "/history")

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)

# hello world