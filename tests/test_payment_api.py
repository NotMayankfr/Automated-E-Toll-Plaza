import json

from etoll import payment_api


def test_register_and_process_payment_store_hashed_sensitive_values(tmp_path, monkeypatch):
    monkeypatch.setattr(payment_api, "DATA_DIR", tmp_path)
    monkeypatch.setattr(payment_api, "VEHICLES_FILE", tmp_path / "vehicles.json")
    monkeypatch.setattr(payment_api, "TRANSACTIONS_FILE", tmp_path / "transactions.json")
    client = payment_api.app.test_client()

    registration = client.post(
        "/register_vehicle",
        json={"vehicle_id": "VH-001", "owner_name": "Asha", "tag_id": "TAG-001", "vehicle_class": "car"},
    )
    payment = client.post(
        "/process_payment",
        json={"vehicle_id": "VH-001", "route": ["Entry-North", "Hub-East"], "amount": 3.5, "payment_token": "tok_demo"},
    )

    assert registration.status_code == 201
    assert payment.status_code == 200
    vehicle = json.loads((tmp_path / "vehicles.json").read_text())[0]
    transaction = json.loads((tmp_path / "transactions.json").read_text())[0]
    assert vehicle["owner_name"] != "Asha"
    assert vehicle["tag_id"] != "TAG-001"
    assert transaction["payment_token"] != "tok_demo"
    assert transaction["amount"] == 3.5


def test_payment_api_rejects_invalid_payloads():
    client = payment_api.app.test_client()
    assert client.post("/register_vehicle", data="not json").status_code == 400
    response = client.post(
        "/process_payment",
        json={"vehicle_id": "VH-001", "route": [], "amount": -1, "payment_token": "token"},
    )
    assert response.status_code == 400
