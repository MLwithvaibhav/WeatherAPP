from flask import Flask, request
from flask_restful import Api, Resource, fields, marshal_with
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from flask import render_template


app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()


API_KEY = "API KEY"
city = "London"  # Default city

weather_fields = {
    "id": fields.Integer,
    "city": fields.String,
    "temperature": fields.Float,
    "description": fields.String,
    "humidity": fields.Integer,
    "wind_speed": fields.Float,
    "pressure": fields.Float,
    "feels_like": fields.Float,
    "timestamp": fields.DateTime
}

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


@app.route("/")
def home():
    return render_template("index.html")

class Weather(Resource):
    @marshal_with(weather_fields)
    def get(self):
        city = request.args.get("city")
        if not city:
            city = "London"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return {"message": "City not found"}, 404

        weather = WeatherModel(
            city=city,
            temperature=data["main"]["temp"],
            description=data["weather"][0]["description"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
            feels_like=data["main"]["feels_like"]
        )

        db.session.add(weather)
        db.session.commit()

        return weather
    

class History(Resource):
    @marshal_with(weather_fields)
    def get(self):
        city = request.args.get("city")
        if not city:
            return {"message": "City is required"}, 400

        records = WeatherModel.query.filter_by(city=city).all()
        if not records:
            return {"message": "No records found for this city"}, 404

        return records
    

class DeleteHistory(Resource):
    def delete(self):
        city = request.args.get("city")
        if not city:
            return {"message": "City is required"}, 400

        records = WeatherModel.query.filter_by(city=city).all()
        if not records:
            return {"message": "No records found for this city"}, 404

        for record in records:
            db.session.delete(record)
        db.session.commit()

        return {"message": f"All records for {city} deleted"}, 200
    
api.add_resource(Weather, "/weather")
api.add_resource(History, "/history")
api.add_resource(DeleteHistory, "/delete_history")

if __name__ == "__main__":
    app.run(debug=True)