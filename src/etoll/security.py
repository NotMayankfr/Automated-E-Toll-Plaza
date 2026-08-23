from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
from typing import Any, Dict


def hash_identifier(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def secure_record(record: Dict[str, Any], sensitive_fields: tuple[str, ...]) -> Dict[str, Any]:
    masked = dict(record)
    for field in sensitive_fields:
        if field in masked and masked[field] is not None:
            masked[field] = hash_identifier(str(masked[field]))
    return masked


def append_json_record(path: Path, record: Dict[str, Any]) -> None:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = []
    payload.append(record)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
