"""Generate deterministic PostgreSQL seed and Neo4j Cypher files.

The live demo seeds through SQLAlchemy on startup. This exporter exists for teams
that want inspectable import artifacts for the container databases.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.database import Base, SessionLocal, engine
from app.models import FirRecord
from app.seed import seed_database


def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_database(db)
        cases = db.query(FirRecord).all()
        out = Path("data/generated"); out.mkdir(parents=True, exist_ok=True)
        sql = ["-- PRAHARI synthetic export; all people/incidents are fictional"]
        cypher = ["// PRAHARI synthetic graph export"]
        for c in cases:
            narrative = c.narrative_en.replace("'", "''")
            sql.append(f"INSERT INTO fir_records (id,fir_number,district,narrative_en) VALUES ('{c.id}','{c.fir_number}','{c.district}','{narrative}');")
            cypher.append(f"MERGE (c:Case {{id:'{c.id}'}}) SET c.cluster='{c.mo_cluster}', c.district='{c.district}';")
        (out / "seed.sql").write_text("\n".join(sql), encoding="utf-8")
        (out / "seed.cypher").write_text("\n".join(cypher), encoding="utf-8")
        print(f"Generated {len(cases)} synthetic FIRs")


if __name__ == "__main__": main()

