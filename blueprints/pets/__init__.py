from flask import Blueprint

pets_bp = Blueprint('pets', __name__)

from . import routes
