from flask import Blueprint

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

from . import routes  # noqa: E402,F401
