import os
os.environ["DATABASE_URL"] = "sqlite:///./data/test_prahari.db"
from fastapi.testclient import TestClient
from app.main import app
from app.intent_parser import reconcile_intent
from app.schemas import Action, Intent, IntentFilters
import re
from uuid import uuid4


def test_health_and_seed():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["cases"] == 500


def test_grounded_chat_and_audit():
    conversation_id = f"test-chain-{uuid4()}"
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "How many IPC 420 cases in Mysuru?", "conversation_id": conversation_id})
        assert response.status_code == 200
        data = response.json()
        allowed = {c["record_id"] for c in data["citations"]}
        cited = set(re.findall(r"\[(FIR-\d{4}-\d{4})\]", data["answer"]))
        assert cited and cited.issubset(allowed)
        chain = client.get(f"/api/audit/{conversation_id}").json()["chain"]
        assert chain and all(entry["verified"] for entry in chain)


def test_kannada_and_similarity():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "ಮೈಸೂರು ಜಿಲ್ಲೆಯಲ್ಲಿ ಎಷ್ಟು ಪ್ರಕರಣಗಳು?", "conversation_id": "kn"})
        assert response.status_code == 200
        assert response.json()["intent"]["language"] == "kn"
        assert response.json()["intent"]["filters"]["district"] == "Mysuru"
        assert response.json()["citations"]
        similar = client.get("/api/cases/FIR-2023-0018/similar")
        assert similar.status_code in (200, 404)


def test_provider_omission_is_reconciled_from_explicit_query():
    provider_intent = Intent(
        filters=IntentFilters(ipc_section="420"),
        requested_action=Action.aggregate,
        language="en",
    )
    reconciled = reconcile_intent(provider_intent, "How many IPC 420 cases in Mysore?")
    assert reconciled.filters.district == "Mysuru"
    assert reconciled.filters.ipc_section == "420"


def test_district_is_not_duplicated_as_station_without_station_cue():
    provider_intent = Intent(
        filters=IntentFilters(district="Mysore", station="Mysore", ipc_section="420"),
        requested_action=Action.aggregate,
        language="en",
    )
    reconciled = reconcile_intent(provider_intent, "How many IPC 420 cases in Mysore?")
    assert reconciled.filters.district == "Mysuru"
    assert reconciled.filters.station is None


def test_linked_cases_and_case_detail_workflow():
    with TestClient(app) as client:
        recent = client.get("/api/dashboard").json()["recent"]
        assert recent
        case_id = recent[0]["id"]
        detail = client.get(f"/api/cases/{case_id}")
        linked = client.get(f"/api/cases/{case_id}/similar")
        assert detail.status_code == 200
        assert detail.json()["id"] == case_id
        assert linked.status_code == 200
        assert linked.json()["source"]["id"] == case_id
        assert isinstance(linked.json()["matches"], list)


def test_fir_ingestion_confirmation_and_validation():
    with TestClient(app) as client:
        accepted = client.post(
            "/api/ingest/scanned-fir",
            data={"language": "kn"},
            files={"file": ("sample.png", b"synthetic-image-content", "image/png")},
        )
        assert accepted.status_code == 200
        assert accepted.json()["status"] == "confirmation_required"
        assert accepted.json()["persisted"] is False
        rejected = client.post(
            "/api/ingest/scanned-fir",
            data={"language": "auto"},
            files={"file": ("unsafe.exe", b"not-a-scan", "application/octet-stream")},
        )
        assert rejected.status_code == 415
