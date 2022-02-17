
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from ..config import config

# Initialize Bootstrap by passing a Flask instance to it in the constructor
bootstrap = Bootstrap()
# Initialize database object
db = SQLAlchemy()

def create_app(config_name='default'):

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) #config[config_name] will transform into Config class static -> Config.init_app(app)

    # initializing variables that were created earlier with no app parameters
    bootstrap.init_app(app)
    db.init_app(app)

    # register bluprint with the app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app