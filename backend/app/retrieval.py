from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session
from .models import FirRecord, Station, User
from .schemas import Action, Intent


def scoped_statement(intent: Intent, user: User | None = None):
    """Trusted parameterized query builder. No model-produced query text enters here."""
    stmt = select(FirRecord, Station).join(Station, FirRecord.station_id == Station.id)
    f = intent.filters
    if f.district: stmt = stmt.where(FirRecord.district == f.district)
    if f.station: stmt = stmt.where(Station.name.ilike(f"%{f.station}%"))
    if f.date_from: stmt = stmt.where(FirRecord.incident_date >= f.date_from)
    if f.date_to: stmt = stmt.where(FirRecord.incident_date <= f.date_to)
    if f.ipc_section: stmt = stmt.where(cast(FirRecord.ipc_sections, String).like(f'%"{f.ipc_section}"%'))
    if f.case_id: stmt = stmt.where(or_(FirRecord.id == f.case_id, FirRecord.fir_number == f.case_id))
    if f.keyword:
        term = f"%{f.keyword}%"
        stmt = stmt.where(or_(FirRecord.narrative_en.ilike(term), FirRecord.weapon.ilike(term), FirRecord.vehicle.ilike(term)))
    if user:
        if user.role in ("constable", "station-SHO") and user.station_id:
            stmt = stmt.where(FirRecord.station_id == user.station_id)
        elif user.role == "district-SP" and user.district:
            stmt = stmt.where(FirRecord.district == user.district)
    return stmt.order_by(FirRecord.incident_date.desc()).limit(100 if intent.requested_action == Action.aggregate else 20)


def retrieve(db: Session, intent: Intent, user: User | None = None) -> list[dict]:
    rows = db.execute(scoped_statement(intent, user)).all()
    return [{"id": fir.id, "fir_number": fir.fir_number, "district": fir.district, "station": station.name, "date": fir.incident_date.isoformat(), "status": fir.status, "outcome": fir.outcome, "narrative_en": fir.narrative_en, "narrative_kn": fir.narrative_kn, "mo_cluster": fir.mo_cluster, "mo_elements": fir.mo_elements, "weapon": fir.weapon, "vehicle": fir.vehicle, "latitude": fir.latitude, "longitude": fir.longitude} for fir, station in rows]


def similar_cases(db: Session, case_id: str, user: User | None = None) -> tuple[dict | None, list[dict]]:
    source = db.get(FirRecord, case_id)
    if not source: return None, []
    intent = Intent()
    candidates = retrieve(db, intent, user)
    ranked = []
    source_elements = set(source.mo_elements)
    for item in candidates:
        if item["id"] == source.id or item["station"] == source.station.name: continue
        shared = sorted(source_elements.intersection(item["mo_elements"]))
        cluster_bonus = 0.45 if item["mo_cluster"] == source.mo_cluster else 0
        score = min(0.99, cluster_bonus + 0.12 * len(shared))
        if score >= 0.45:
            item = {**item, "similarity": round(score, 2), "shared_elements": shared}
            ranked.append(item)
    return {"id": source.id, "fir_number": source.fir_number}, sorted(ranked, key=lambda x: x["similarity"], reverse=True)[:8]

