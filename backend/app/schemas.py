from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class Action(str, Enum):
    lookup = "lookup"
    aggregate = "aggregate"
    network = "network"
    similarity = "similarity"


class IntentFilters(BaseModel):
    district: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    ipc_section: str | None = None
    station: str | None = None
    keyword: str | None = None
    case_id: str | None = None


class Intent(BaseModel):
    entity_type: str = "case"
    relation: str | None = None
    filters: IntentFilters = Field(default_factory=IntentFilters)
    requested_action: Action = Action.lookup
    language: str = "en"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str = Field(min_length=1, max_length=80)
    language: str | None = None


class Citation(BaseModel):
    record_id: str
    fir_number: str
    district: str
    station: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: str
    intent: Intent
    audit_id: int

