from flask import Flask, request
from flask_restful import Api, Resource, fields, marshal_with
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests   # <-- yaha se requests use karna hai
from flask import render_template

app = Flask(__name__)
CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

API_KEY = "API KEY"   # <-- yaha apni API key daal
city = "London"  # Default city
# ------------------------------
# Database Model
# ------------------------------
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

# ------------------------------
# Marshalling fields
# ------------------------------
weather_fields = {
    "id": fields.Integer,
    "city": fields.String,
    "temperature": fields.Float,
    "description": fields.String,
    "humidity": fields.Integer,
    "wind_speed": fields.Float,
    "pressure": fields.Float,
    "feels_like": fields.Float,   # <-- yaha spelling sahi kiya
    "timestamp": fields.DateTime
}

# ------------------------------
# Weather Resource
# ------------------------------

@app.route("/")
def home():
    return render_template("index.html")


class Weather(Resource):
    @marshal_with(weather_fields)
    def get(self):
        city = request.args.get("city")   # query string se city lena
        if not city:
            return {"message": "City is required"}, 400

        # OpenWeather API call
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()

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

# ------------------------------
# History Resource
# ------------------------------
class History(Resource):
    @marshal_with(weather_fields)
    def get(self):
        records = WeatherModel.query.all()
        return records, 200

# ------------------------------
# Delete Resource
# ------------------------------
class DeleteHistory(Resource):
    def delete(self, record_id):
        record = WeatherModel.query.get(record_id)
        if not record:
            return {"message": "Record not found"}, 404

        db.session.delete(record)
        db.session.commit()
        return {"message": "Record deleted successfully"}, 200

# ------------------------------
# Routes
# ------------------------------
api.add_resource(Weather, "/weather")
api.add_resource(History, "/history")
api.add_resource(DeleteHistory, "/history/<int:record_id>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # table create karega agar nahi hai
    app.run(debug=True)

#hello world 
#hello world