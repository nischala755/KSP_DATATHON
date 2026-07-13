import base64
import json
import re

import httpx

from .config import get_settings


class OCRConfigurationError(RuntimeError):
    pass


def _fallback_fields(markdown: str) -> dict:
    """Best-effort extraction when OCR succeeds but structured mapping does not."""
    def find_label(label: str) -> str | None:
        patterns = (
            rf"(?:{label})\s*:?\s*\|\s*([^|\n]+)",
            rf"(?:{label})\s*:\s*([^|\n]+)",
        )
        for pattern in patterns:
            match = re.search(pattern, markdown, re.I | re.M)
            if match:
                return match.group(1).strip(" *|:#-")
        return None

    sections = find_label(r"(?:IPC\s*)?Sections?|ಸೆಕ್ಷನ್(?:ಗಳು)?")
    return {
        "fir_number": find_label(r"FIR\s*(?:ID|No\.?|Number)?|ಪ್ರಕರಣ\s*ಸಂಖ್ಯೆ"),
        "station": find_label(r"Police\s*Station|Station|ಪೊಲೀಸ್\s*ಠಾಣೆ"),
        "district": find_label(r"District|ಜಿಲ್ಲೆ"),
        "date": find_label(r"Date|ದಿನಾಂಕ"),
        "sections": [item.strip() for item in re.split(r"[,;]", sections)] if sections else [],
        "complainant": find_label(r"Complainant|ದೂರುದಾರ"),
        "narrative": markdown[:6000],
    }


async def _structure_fir(client: httpx.AsyncClient, api_key: str, markdown: str) -> dict:
    prompt = """Extract FIR review fields from the OCR text. Return JSON only with keys:
fir_number, station, district, date, sections (array of strings), complainant, narrative.
Copy only values present in the OCR text. Use null or [] when absent. Do not infer identities,
addresses, offences, or facts. Preserve Kannada text when present.

OCR TEXT:
""" + markdown[:12000]
    response = await client.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "mistral-small-latest",
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "You map OCR text to a strict review JSON object without adding facts."},
                {"role": "user", "content": prompt},
            ],
        },
    )
    response.raise_for_status()
    data = json.loads(response.json()["choices"][0]["message"]["content"])
    fallback = _fallback_fields(markdown)
    return {
        "fir_number": data.get("fir_number") or fallback["fir_number"],
        "station": data.get("station") or fallback["station"],
        "district": data.get("district") or fallback["district"],
        "date": data.get("date") or fallback["date"],
        "sections": data.get("sections") if isinstance(data.get("sections"), list) else fallback["sections"],
        "complainant": data.get("complainant") or fallback["complainant"],
        "narrative": data.get("narrative") or fallback["narrative"],
    }


async def ocr_fir_document(content: bytes, content_type: str, requested_language: str) -> dict:
    settings = get_settings()
    if not settings.mistral_api_key:
        raise OCRConfigurationError("MISTRAL_API_KEY is not configured")

    encoded = base64.b64encode(content).decode("ascii")
    data_url = f"data:{content_type};base64,{encoded}"
    is_pdf = content_type == "application/pdf"
    document = (
        {"type": "document_url", "document_url": data_url}
        if is_pdf else
        {"type": "image_url", "image_url": data_url}
    )
    headers = {"Authorization": f"Bearer {settings.mistral_api_key}"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=20.0)) as client:
        response = await client.post(
            "https://api.mistral.ai/v1/ocr",
            headers=headers,
            json={
                "model": "mistral-ocr-latest",
                "document": document,
                "include_image_base64": False,
                "confidence_scores_granularity": "page",
            },
        )
        response.raise_for_status()
        payload = response.json()
        pages = payload.get("pages") or []
        markdown = "\n\n".join(page.get("markdown", "") for page in pages).strip()
        if not markdown:
            raise ValueError("Mistral OCR returned no text")
        try:
            fields = await _structure_fir(client, settings.mistral_api_key, markdown)
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            fields = _fallback_fields(markdown)

    detected_language = requested_language
    if requested_language == "auto":
        detected_language = "kn" if re.search(r"[\u0C80-\u0CFF]", markdown) else "en"
    confidence_values = [
        page.get("confidence_scores", {}).get("average_page_confidence_score")
        for page in pages
        if page.get("confidence_scores", {}).get("average_page_confidence_score") is not None
    ]
    return {
        "language": detected_language,
        "extracted": {**fields, "raw_text": markdown},
        "ocr": {
            "provider": "mistral",
            "model": payload.get("model", "mistral-ocr-latest"),
            "pages": len(pages),
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 3) if confidence_values else None,
        },
    }
