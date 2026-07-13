import hashlib
import random
from datetime import date, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import CasePerson, FirRecord, Person, Station, User

DISTRICTS = ["Bengaluru Urban", "Mysuru", "Belagavi", "Mangaluru", "Shivamogga", "Tumakuru", "Dharwad", "Ballari", "Kalaburagi", "Udupi", "Hassan", "Mandya", "Kodagu", "Kolar", "Davanagere"]
MO_PATTERNS = [
    ("night-housebreak", ["rear-window entry", "night-time", "jewellery targeted"], "iron rod"),
    ("highway-cargo", ["highway interception", "false police signal", "cargo targeted"], "knife"),
    ("atm-distraction", ["ATM vestibule", "card distraction", "shoulder surfing"], None),
    ("temple-donation", ["temple premises", "lock cutting", "donation box targeted"], "bolt cutter"),
    ("warehouse-entry", ["roof entry", "CCTV disabled", "electronics targeted"], "crowbar"),
    ("bike-chain", ["motorcycle approach", "evening-time", "jewellery targeted"], None),
    ("cyber-otp", ["impersonated bank officer", "OTP requested", "mule account"], None),
    ("farm-pump", ["agricultural land", "copper wiring targeted", "night-time"], "wire cutter"),
    ("bus-pickpocket", ["crowded bus", "wallet targeted", "multiple offenders"], None),
    ("shop-shutter", ["shutter forced", "early morning", "cash drawer targeted"], "crowbar"),
    ("vehicle-theft", ["duplicate key", "parking area", "two-wheeler targeted"], None),
    ("courier-fraud", ["fake courier call", "threat of prosecution", "digital transfer"], None),
    ("cattle-theft", ["rural road", "goods vehicle", "night-time"], None),
    ("construction-theft", ["construction site", "power tools targeted", "weekend"], "bolt cutter"),
    ("phone-snatch", ["motorcycle approach", "phone targeted", "bus stop"], None),
    ("office-breakin", ["duplicate access card", "office premises", "laptop targeted"], None),
    ("fuel-card", ["fleet card cloned", "multiple fuel stations", "night-time"], None),
    ("market-purse", ["crowded market", "distraction", "purse targeted"], None),
]


def password_hash(password: str) -> str:
    return hashlib.sha256(("prahari-demo:" + password).encode()).hexdigest()


def seed_database(db: Session, count: int = 500) -> None:
    if db.scalar(select(func.count(FirRecord.id))): return
    rng = random.Random(20260713)
    stations = []
    for i, district in enumerate(DISTRICTS):
        station = Station(name=f"{district.split()[0]} Central PS", district=district, latitude=12.1 + i * .18, longitude=74.9 + i * .23)
        db.add(station); stations.append(station)
    db.flush()
    statuses = ["Under Investigation", "Charge Sheet Filed", "Closed", "Trial Pending"]
    for n in range(1, count + 1):
        station = stations[n % len(stations)]
        cluster, elements, weapon = MO_PATTERNS[n % len(MO_PATTERNS)]
        incident_date = date(2023, 1, 1) + timedelta(days=rng.randrange(0, 1200))
        vehicle = "fictional grey motorcycle KA-00-X-0000" if "motorcycle approach" in elements else None
        fid = f"FIR-{incident_date.year}-{n:04d}"
        narrative = f"Synthetic training case: unknown fictional persons used {', '.join(elements)}. No real person or incident is represented."
        fir = FirRecord(id=fid, fir_number=f"{n:04d}/{incident_date.year}", station_id=station.id, district=station.district, incident_date=incident_date, ipc_sections=[rng.choice(["379", "380", "420", "457", "392"])], narrative_en=narrative, narrative_kn=f"ಸಂಶ್ಲೇಷಿತ ತರಬೇತಿ ಪ್ರಕರಣ: {cluster} ವಿಧಾನ. ಇದು ನೈಜ ಘಟನೆ ಅಲ್ಲ.", latitude=station.latitude + rng.uniform(-.12, .12), longitude=station.longitude + rng.uniform(-.12, .12), status=rng.choice(statuses), outcome=rng.choice(["Pending", "Property recovered", "Charge sheet submitted", "Insufficient evidence"]), mo_cluster=cluster, mo_elements=elements, weapon=weapon, vehicle=vehicle)
        db.add(fir)
        if n <= 120:
            person = Person(fictional_name=f"Fictional Person {n:03d}")
            db.add(person); db.flush(); db.add(CasePerson(case_id=fid, person_id=person.id, role=rng.choice(["accused", "victim", "witness"])))
    db.flush()
    demo_users = [
        ("constable", "constable", stations[0].district, stations[0].id),
        ("sho", "station-SHO", stations[0].district, stations[0].id),
        ("sp", "district-SP", stations[1].district, None),
        ("admin", "SCRB-admin", None, None),
    ]
    for username, role, district, station_id in demo_users:
        db.add(User(username=username, password_hash=password_hash("demo1234"), role=role, district=district, station_id=station_id))
    db.commit()

