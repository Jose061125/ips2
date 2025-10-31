from datetime import date
from app import create_app


def make_app():
    return create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })


def test_list_patients_empty():
    app = make_app()
    with app.test_client() as client:
        r = client.get("/api/v1/patients")
        assert r.status_code == 200
        data = r.get_json()
        assert data["total"] == 0
        assert data["items"] == []


def test_create_patient_and_list():
    app = make_app()
    payload = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "document": "DOC12345",
        "email": "ana@example.com",
        "phone": "3001234567",
        "address": "Calle 123",
        "birth_date": date(1990, 5, 17).isoformat(),
    }
    with app.test_client() as client:
        r = client.post("/api/v1/patients", json=payload)
        assert r.status_code == 201
        created = r.get_json()
        assert created["id"] > 0
        assert created["first_name"] == "Ana"
        assert created["document"] == "DOC12345"

        # List should return 1
        r2 = client.get("/api/v1/patients")
        assert r2.status_code == 200
        data = r2.get_json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["document"] == "DOC12345"


def test_create_patient_conflict_document():
    app = make_app()
    payload = {
        "first_name": "Ana",
        "last_name": "Gomez",
        "document": "UNIQ001",
    }
    with app.test_client() as client:
        r1 = client.post("/api/v1/patients", json=payload)
        assert r1.status_code == 201
        r2 = client.post("/api/v1/patients", json=payload)
        assert r2.status_code == 409
        assert "unique" in r2.get_json()["error"]
