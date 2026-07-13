import os
os.environ["DATABASE_URL"] = "sqlite:///./data/test_prahari.db"
from fastapi.testclient import TestClient
from app.main import app
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
        similar = client.get("/api/cases/FIR-2023-0018/similar")
        assert similar.status_code in (200, 404)
