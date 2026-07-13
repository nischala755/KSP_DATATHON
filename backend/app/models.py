from datetime import datetime, timezone
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Station(Base):
    __tablename__ = "stations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


class FirRecord(Base):
    __tablename__ = "fir_records"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    fir_number: Mapped[str] = mapped_column(String(40), unique=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    district: Mapped[str] = mapped_column(String(80), index=True)
    incident_date: Mapped[datetime] = mapped_column(Date, index=True)
    ipc_sections: Mapped[list] = mapped_column(JSON)
    narrative_en: Mapped[str] = mapped_column(Text)
    narrative_kn: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(40))
    outcome: Mapped[str] = mapped_column(String(120))
    mo_cluster: Mapped[str] = mapped_column(String(40), index=True)
    mo_elements: Mapped[list] = mapped_column(JSON)
    weapon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    vehicle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    station: Mapped[Station] = relationship()


class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    fictional_name: Mapped[str] = mapped_column(String(100))


class CasePerson(Base):
    __tablename__ = "case_persons"
    case_id: Mapped[str] = mapped_column(ForeignKey("fir_records.id"), primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), primary_key=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30))
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(80), index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    query: Mapped[str] = mapped_column(Text)
    intent: Mapped[dict] = mapped_column(JSON)
    record_ids: Mapped[list] = mapped_column(JSON)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    previous_hash: Mapped[str] = mapped_column(String(64))
    entry_hash: Mapped[str] = mapped_column(String(64), unique=True)
    signature: Mapped[str] = mapped_column(String(64))
