from __future__ import annotations

from datetime import datetime, UTC
import math
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, request

from etoll.security import append_json_record, secure_record


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
VEHICLES_FILE = DATA_DIR / "vehicles.json"

app = Flask(__name__)


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _json_object() -> tuple[Dict[str, object] | None, tuple[object, int] | None]:
    """Return a JSON request object or a consistent client error response."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "request body must be a JSON object"}), 400)
    return payload, None


@app.get("/health")
def health() -> tuple[Dict[str, str], int]:
    return {"status": "ok", "timestamp": _timestamp()}, 200


@app.post("/register_vehicle")
def register_vehicle():
    payload, error = _json_object()
    if error:
        return error
    assert payload is not None
    required = {"vehicle_id", "owner_name", "tag_id", "vehicle_class"}
    missing = sorted(required - payload.keys())
    if missing:
        return jsonify({"error": "missing fields", "fields": missing}), 400

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    record = secure_record(
        {
            "vehicle_id": payload["vehicle_id"],
            "owner_name": payload["owner_name"],
            "tag_id": payload["tag_id"],
            "vehicle_class": payload["vehicle_class"],
            "created_at": _timestamp(),
        },
        sensitive_fields=("owner_name", "tag_id"),
    )
    append_json_record(VEHICLES_FILE, record)
    return jsonify({"message": "vehicle registered", "vehicle_id": payload["vehicle_id"]}), 201


@app.post("/process_payment")
def process_payment():
    payload, error = _json_object()
    if error:
        return error
    assert payload is not None
    required = {"vehicle_id", "route", "amount", "payment_token"}
    missing = sorted(required - payload.keys())
    if missing:
        return jsonify({"error": "missing fields", "fields": missing}), 400

    if not isinstance(payload["route"], list) or not payload["route"] or not all(isinstance(node, str) for node in payload["route"]):
        return jsonify({"error": "route must be a non-empty list of location names"}), 400
    try:
        amount = float(payload["amount"])
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400
    if not math.isfinite(amount) or amount <= 0:
        return jsonify({"error": "amount must be greater than zero"}), 400

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    record = secure_record(
        {
            "vehicle_id": payload["vehicle_id"],
            "route": payload["route"],
            "amount": round(amount, 2),
            "payment_token": payload["payment_token"],
            "status": "approved",
            "processed_at": _timestamp(),
        },
        sensitive_fields=("payment_token",),
    )
    append_json_record(TRANSACTIONS_FILE, record)
    return jsonify({"message": "payment approved", "vehicle_id": payload["vehicle_id"], "amount": record["amount"]}), 200


@app.get("/transactions")
def transactions():
    if not TRANSACTIONS_FILE.exists():
        return jsonify([])
    return app.response_class(TRANSACTIONS_FILE.read_text(encoding="utf-8"), mimetype="application/json")


if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=8443, debug=True, ssl_context="adhoc")
