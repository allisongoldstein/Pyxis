# from msilib.schema import AppId
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import models
from app.routes import routes

from app.routes import user
app.register_blueprint(user.bp)

from app.routes import cards
app.register_blueprint(cards.bp)

from app.routes import targets
app.register_blueprint(targets.bp)

from app.routes import maps
app.register_blueprint(maps.bp)
