from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from decouple import config
from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://www.slink.lat"}})
app.config.from_object(config("APP_SETTINGS"))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

jwt = JWTManager(app)
