
# from pkgutil import ImpImporter
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from ..config import config
from flask_mail import Mail
from flask_moment import Moment

# Initialize Bootstrap by passing a Flask instance to it in the constructor
bootstrap = Bootstrap()
# Initialize database object
db = SQLAlchemy()
# Initialize the Login manager object
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # View to redirect if @login_required
# Initialize the Mail object
mail = Mail()
# Moment object will help convert time to user's local time
moment = Moment()

def create_app(config_name='default'):

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) #config[config_name] will transform into Config class static -> Config.init_app(app)

    # initializing variables that were created earlier with no app parameters
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # register bluprints with the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app