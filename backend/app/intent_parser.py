import json
import re
from abc import ABC, abstractmethod
import httpx
from .config import get_settings
from .schemas import Action, Intent, IntentFilters

DISTRICTS = ["Bengaluru Urban", "Mysuru", "Belagavi", "Mangaluru", "Shivamogga", "Tumakuru", "Dharwad", "Ballari", "Kalaburagi", "Udupi", "Hassan", "Mandya", "Kodagu", "Kolar", "Davanagere"]
DISTRICT_ALIASES = {
    "bangalore": "Bengaluru Urban",
    "bengaluru": "Bengaluru Urban",
    "ಬೆಂಗಳೂರು": "Bengaluru Urban",
    "mysore": "Mysuru",
    "mysuru": "Mysuru",
    "ಮೈಸೂರು": "Mysuru",
    "belgaum": "Belagavi",
    "ಬೆಳಗಾವಿ": "Belagavi",
    "mangalore": "Mangaluru",
    "ಮಂಗಳೂರು": "Mangaluru",
    "shimoga": "Shivamogga",
    "ಶಿವಮೊಗ್ಗ": "Shivamogga",
    "tumkur": "Tumakuru",
    "ತುಮಕೂರು": "Tumakuru",
    "bellary": "Ballari",
    "ಬಳ್ಳಾರಿ": "Ballari",
    "gulbarga": "Kalaburagi",
    "ಕಲಬುರಗಿ": "Kalaburagi",
}


def normalize_intent(intent: Intent) -> Intent:
    """Canonicalize provider vocabulary without broadening query authority."""
    district = intent.filters.district
    if district:
        canonical = next((item for item in DISTRICTS if item.casefold() == district.casefold()), None)
        intent.filters.district = canonical or DISTRICT_ALIASES.get(district.strip().casefold(), district)
    return intent


def canonical_district(value: str | None) -> str | None:
    if not value:
        return None
    return next((item for item in DISTRICTS if item.casefold() == value.strip().casefold()), None) or DISTRICT_ALIASES.get(value.strip().casefold())


def reconcile_intent(intent: Intent, query: str, language: str | None = None) -> Intent:
    """Fill provider omissions only with filters deterministically present in the query."""
    intent = normalize_intent(intent)
    fallback = local_parse(query, language)
    for field in ("district", "date_from", "date_to", "ipc_section", "station", "keyword", "case_id"):
        if getattr(intent.filters, field) is None:
            setattr(intent.filters, field, getattr(fallback.filters, field))
    station_as_district = canonical_district(intent.filters.station)
    has_station_cue = bool(re.search(r"\b(?:police\s+station|station|p\.?s\.?)\b|ಠಾಣೆ", query, re.I))
    if station_as_district == intent.filters.district and not has_station_cue:
        intent.filters.station = None
    return normalize_intent(intent)


def detect_language(text: str) -> str:
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kn"
    return "kanglish" if any(x in text.lower().split() for x in ("yaava", "eshtu", "prakarana", "torisu")) else "en"


def local_parse(query: str, language: str | None = None) -> Intent:
    """Deterministic fallback. It intentionally supports a narrow, auditable vocabulary."""
    lowered = query.lower()
    filters = IntentFilters()
    for district in DISTRICTS:
        if district.lower() in lowered:
            filters.district = district
            break
    if not filters.district:
        for alias, district in DISTRICT_ALIASES.items():
            if alias in lowered:
                filters.district = district
                break
    section = re.search(r"(?:ipc|section|ಸೆಕ್ಷನ್)\s*[-:]?\s*(\d{2,3}[a-z]?)", lowered)
    if section:
        filters.ipc_section = section.group(1).upper()
    case_id = re.search(r"(?:case|fir|ಪ್ರಕರಣ)\s*(?:id|number|no\.?)?\s*[:#-]?\s*(FIR-\d{4}-\d{4})", query, re.I)
    if case_id:
        filters.case_id = case_id.group(1).upper()
    year = re.search(r"\b(202[3-6])\b", lowered)
    if year:
        from datetime import date
        filters.date_from, filters.date_to = date(int(year.group(1)), 1, 1), date(int(year.group(1)), 12, 31)
    action = Action.lookup
    if any(x in lowered for x in ("how many", "count", "trend", "ಎಷ್ಟು", "ಸಂಖ್ಯೆ")):
        action = Action.aggregate
    elif any(x in lowered for x in ("similar", "same mo", "ಹೋಲುವ", "ಒಂದೇ ವಿಧಾನ")):
        action = Action.similarity
    elif any(x in lowered for x in ("network", "linked", "connection", "ಸಂಬಂಧ")):
        action = Action.network
    keyword_terms = ["motorcycle", "jewellery", "warehouse", "knife", "ATM", "temple", "cyber"]
    for term in keyword_terms:
        if term.lower() in lowered:
            filters.keyword = term
            break
    return normalize_intent(Intent(filters=filters, requested_action=action, language=language or detect_language(query)))


SYSTEM_PROMPT = """You parse police analytical questions into JSON only. Never emit SQL or Cypher.
Schema: {entity_type:'case', relation:null|string, filters:{district,date_from,date_to,ipc_section,station,keyword,case_id}, requested_action:'lookup'|'aggregate'|'network'|'similarity', language:'en'|'kn'|'kanglish'}.
Only copy filters explicitly present in the question. Unknown values must be null."""


class LLMProvider(ABC):
    @abstractmethod
    async def parse_intent(self, query: str, language: str | None = None) -> Intent: ...

    async def generate_answer(self, intent: Intent, records: list[dict]) -> str:
        return grounded_local_answer(intent, records)


class MockProvider(LLMProvider):
    async def parse_intent(self, query: str, language: str | None = None) -> Intent:
        return local_parse(query, language)


class MistralProvider(LLMProvider):
    def __init__(self, api_key: str): self.api_key = api_key

    async def parse_intent(self, query: str, language: str | None = None) -> Intent:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post("https://api.mistral.ai/v1/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": "mistral-small-latest", "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": query}]})
                response.raise_for_status()
                parsed = Intent.model_validate(json.loads(response.json()["choices"][0]["message"]["content"]))
                return reconcile_intent(parsed, query, language)
        except Exception:
            return local_parse(query, language)


class SarvamProvider(LLMProvider):
    def __init__(self, api_key: str): self.api_key = api_key

    async def parse_intent(self, query: str, language: str | None = None) -> Intent:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post("https://api.sarvam.ai/v1/chat/completions", headers={"api-subscription-key": self.api_key}, json={"model": "sarvam-m", "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": query}]})
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return reconcile_intent(Intent.model_validate(json.loads(content)), query, language)
        except Exception:
            return local_parse(query, language)


def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider.lower() == "mistral" and settings.mistral_api_key:
        return MistralProvider(settings.mistral_api_key)
    if settings.llm_provider.lower() == "sarvam" and settings.sarvam_api_key:
        return SarvamProvider(settings.sarvam_api_key)
    return MockProvider()


def grounded_local_answer(intent: Intent, records: list[dict]) -> str:
    kn = intent.language == "kn"
    if not records:
        return "ಈ ಮಾಹಿತಿಯು ಲಭ್ಯವಿಲ್ಲ." if kn else "I don't have that information in the retrieved records."
    ids = ", ".join(f"[{r['id']}]" for r in records[:5])
    if intent.requested_action == Action.aggregate:
        return (f"ಪರಿಶೀಲಿಸಿದ ದಾಖಲೆಗಳಲ್ಲಿ {len(records)} ಹೊಂದಾಣಿಕೆಯ ಪ್ರಕರಣಗಳಿವೆ: {ids}." if kn else f"The retrieved records contain {len(records)} matching cases: {ids}.")
    if intent.requested_action == Action.similarity:
        top = records[0]
        elements = ", ".join(top.get("mo_elements", []))
        return (f"ಹೋಲುವ ಪ್ರಕರಣಗಳು {ids}. ಸಾಮಾನ್ಯ ವಿಧಾನಗಳು: {elements}." if kn else f"Similar cases are {ids}. Shared MO elements include: {elements}.")
    summaries = "; ".join(f"{r['fir_number']} at {r['station']} ({r['status']}) [{r['id']}]" for r in records[:5])
    return (f"ದಾಖಲೆಗಳ ಆಧಾರದಲ್ಲಿ: {summaries}." if kn else f"Based on the retrieved records: {summaries}.")
