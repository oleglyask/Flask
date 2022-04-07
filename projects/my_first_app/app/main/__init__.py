from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

from . import views, errors

# Allows the Permision class to be seen GLOBALY including in templates
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)