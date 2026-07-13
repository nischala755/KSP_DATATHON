from contextlib import asynccontextmanager
from pathlib import Path
import os
import httpx
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from .audit import append_audit, verify_chain
from .auth import authenticate, create_token, current_user
from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .intent_parser import get_provider
from .models import AuditLog, FirRecord, User
from .ocr import OCRConfigurationError, ocr_fir_document
from .retrieval import retrieve, similar_cases
from .schemas import ChatRequest, ChatResponse, Citation
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path("data").mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
    with SessionLocal() as db: seed_database(db)
    yield


app = FastAPI(title="PRAHARI API", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok", "cases": len(db.scalars(select(FirRecord.id)).all()), "llm_provider": settings.llm_provider}


@app.post("/api/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form.username, form.password)
    if not user: raise HTTPException(401, "Incorrect username or password")
    return {"access_token": create_token(user), "token_type": "bearer", "role": user.role, "username": user.username}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    intent = await get_provider().parse_intent(body.message, body.language)
    records = retrieve(db, intent, user)
    answer = await get_provider().generate_answer(intent, records)
    record_ids = [r["id"] for r in records]
    # The local generator cites only retrieved records; any future remote generator must pass this check.
    import re
    cited = set(re.findall(r"\[(FIR-\d{4}-\d{4})\]", answer))
    if not cited.issubset(set(record_ids)):
        raise HTTPException(502, "Grounding check rejected an unknown citation")
    audit = append_audit(db, body.conversation_id, user.id if user else None, body.message, intent.model_dump(mode="json"), record_ids, answer)
    citations = [Citation(record_id=r["id"], fir_number=r["fir_number"], district=r["district"], station=r["station"]) for r in records[:8]]
    confidence = "high" if len(records) >= 3 else "medium" if records else "low"
    return ChatResponse(answer=answer, citations=citations, confidence=confidence, intent=intent, audit_id=audit.id)


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)):
    row = db.get(FirRecord, case_id)
    if not row: raise HTTPException(404, "Case not found")
    return {"id": row.id, "fir_number": row.fir_number, "district": row.district, "station": row.station.name, "date": row.incident_date, "ipc_sections": row.ipc_sections, "narrative_en": row.narrative_en, "narrative_kn": row.narrative_kn, "status": row.status, "outcome": row.outcome, "mo_elements": row.mo_elements, "latitude": row.latitude, "longitude": row.longitude}


@app.get("/api/cases/{case_id}/similar")
def get_similar(case_id: str, db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    source, matches = similar_cases(db, case_id, user)
    if not source: raise HTTPException(404, "Case not found")
    return {"source": source, "matches": matches, "method": "explainable synthetic-MO overlap; production embedding adapter is scoped"}


@app.get("/api/audit/{conversation_id}")
def audit(conversation_id: str, db: Session = Depends(get_db)):
    rows = list(db.scalars(select(AuditLog).where(AuditLog.conversation_id == conversation_id).order_by(AuditLog.id)))
    return {"conversation_id": conversation_id, "chain": verify_chain(rows), "signature_scheme": "HMAC-SHA256 demo fallback; ML-DSA required in production"}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), user: User | None = Depends(current_user)):
    records = retrieve(db, __import__("app.schemas", fromlist=["Intent"]).Intent(), user)
    by_district = {}
    for row in records: by_district[row["district"]] = by_district.get(row["district"], 0) + 1
    return {"total_visible": len(records), "by_district": [{"district": k, "count": v} for k, v in sorted(by_district.items())], "recent": records[:6], "fairness_note": "Only area-level aggregates are shown. PRAHARI does not produce individual risk scores."}


@app.post("/api/ingest/scanned-fir")
async def ingest_scanned_fir(file: UploadFile = File(...), language: str = Form("auto")):
    allowed_types = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(415, "Only PDF, PNG, JPG, and WEBP FIR scans are supported")
    if language not in {"auto", "en", "kn"}:
        raise HTTPException(400, "Language must be auto, en, or kn")
    content = await file.read(10 * 1024 * 1024 + 1)
    if not content: raise HTTPException(400, "Empty file")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "File exceeds the 10 MB upload limit")
    try:
        result = await ocr_fir_document(content, file.content_type, language)
    except OCRConfigurationError as exc:
        raise HTTPException(503, str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(502, f"Mistral OCR request failed with status {exc.response.status_code}") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, "Mistral OCR could not process this document") from exc
    return {
        "status": "confirmation_required",
        "filename": file.filename,
        **result,
        "persisted": False,
        "scope_note": "Mistral OCR extraction completed. An authorized operator must verify every field before persistence.",
    }


# AppSail deployment serves the compiled React client from the same origin as
# the API. API routes remain registered first, so the SPA fallback cannot
# shadow them.
static_dir = Path(os.getenv("PRAHARI_STATIC_DIR", "frontend_dist"))
if static_dir.exists():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend_spa(full_path: str):
        requested = static_dir / full_path
        if full_path and requested.is_file() and static_dir.resolve() in requested.resolve().parents:
            return FileResponse(requested)
        return FileResponse(static_dir / "index.html")
