from flask import Blueprint
from ..models import Permission, ReleaseType

main = Blueprint('main', __name__)

from . import views, errors

# Allows the Permision class to be seen GLOBALY including in templates
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

# Allows the ReleaseType class to be seen GLOBALY including in templates
@main.app_context_processor
def inject_releaseTypes():
    return dict(ReleaseType=ReleaseType)