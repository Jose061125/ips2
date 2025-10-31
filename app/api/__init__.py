from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.get("/health")
def health():
    now = datetime.now(timezone.utc).isoformat()
    version = current_app.config.get("APP_VERSION", "1.2.0")
    return jsonify({
        "status": "ok",
        "version": version,
        "timestamp": now,
    }), 200
