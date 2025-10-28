from flask import Blueprint

records_bp = Blueprint('records', __name__, url_prefix='/records')

from . import routes  # noqa: E402,F401
