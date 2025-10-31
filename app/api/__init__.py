from flask import Blueprint, jsonify, current_app, request
from datetime import datetime, timezone
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, validates, ValidationError
from ..models import db, Patient

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


class PatientSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    document = fields.Str(required=True)
    birth_date = fields.Date(allow_none=True)
    phone = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    address = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    @validates("document")
    def validate_document(self, value: str, **kwargs):
        if not value or len(value) < 5:
            raise ValidationError("document must be at least 5 characters")


patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)


@api_bp.get("/patients")
def list_patients():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        q = (request.args.get("q") or "").strip()
    except ValueError:
        return jsonify({"error": "invalid pagination params"}), 400

    query = Patient.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Patient.first_name.ilike(like),
            Patient.last_name.ilike(like),
            Patient.document.ilike(like),
        ))

    total = query.count()
    items = query.order_by(Patient.created_at.desc()) 
    items = items.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "items": patients_schema.dump(items),
        "total": total,
        "page": page,
        "per_page": per_page,
    }), 200


@api_bp.post("/patients")
def create_patient():
    # Expect JSON payload
    if not request.is_json:
        return jsonify({"error": "content-type must be application/json"}), 415
    try:
        data = patient_schema.load(request.get_json() or {})
    except ValidationError as ve:
        return jsonify({"errors": ve.messages}), 422

    patient = Patient(**data)
    db.session.add(patient)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "document must be unique"}), 409

    return jsonify(patient_schema.dump(patient)), 201
