import hashlib
import hmac
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .models import AuditLog


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()


def append_audit(db: Session, conversation_id: str, user_id: int | None, query: str, intent: dict, record_ids: list[str], answer: str) -> AuditLog:
    previous = db.scalar(select(AuditLog).where(AuditLog.conversation_id == conversation_id).order_by(AuditLog.id.desc()).limit(1))
    previous_hash = previous.entry_hash if previous else "0" * 64
    payload = {"conversation_id": conversation_id, "user_id": user_id, "query": query, "intent": intent, "record_ids": record_ids, "answer": answer, "previous_hash": previous_hash}
    entry_hash = hashlib.sha256(_canonical(payload)).hexdigest()
    # TODO: swap for ML-DSA in production when liboqs-python is available.
    signature = hmac.new(get_settings().audit_signing_key.encode(), entry_hash.encode(), hashlib.sha256).hexdigest()
    row = AuditLog(**payload, entry_hash=entry_hash, signature=signature)
    db.add(row); db.commit(); db.refresh(row)
    return row


def verify_chain(rows: list[AuditLog]) -> list[dict]:
    previous = "0" * 64
    key = get_settings().audit_signing_key.encode()
    result = []
    for row in rows:
        signature_ok = hmac.compare_digest(row.signature, hmac.new(key, row.entry_hash.encode(), hashlib.sha256).hexdigest())
        link_ok = row.previous_hash == previous
        result.append({"id": row.id, "query": row.query, "intent": row.intent, "record_ids": row.record_ids, "answer": row.answer, "timestamp": row.created_at.isoformat(), "entry_hash": row.entry_hash, "verified": signature_ok and link_ok})
        previous = row.entry_hash
    return result

