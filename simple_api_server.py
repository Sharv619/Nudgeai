#!/usr/bin/env python3
"""
Canonical MVP API server for NudgeAI.

This server owns the V0/V1 manual nudge loop. Older data/RAG/MCP endpoints remain
available below as local prototype/experimental endpoints, but they are not the
canonical MVP product path.
"""

import json
import logging
import math
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NudgeAI MVP API")

NUDGE_STORE_PATH = Path(os.getenv("NUDGE_STORE_PATH", "data/nudges.json"))
PLACES_STORE_PATH = Path(os.getenv("PLACES_STORE_PATH", "data/places.json"))
CONTEXT_RULES_STORE_PATH = Path(os.getenv("CONTEXT_RULES_STORE_PATH", "data/context_rules.json"))
RULE_STATE_STORE_PATH = Path(os.getenv("RULE_STATE_STORE_PATH", "data/rule_state.json"))
CURRENT_LOCATION_STORE_PATH = Path(os.getenv("CURRENT_LOCATION_STORE_PATH", "data/current_location.json"))
CALENDAR_AVAILABILITY_STORE_PATH = Path(os.getenv("CALENDAR_AVAILABILITY_STORE_PATH", "data/calendar_availability.json"))
NUDGE_STATUSES = {"pending", "snoozed", "completed", "dismissed"}
NUDGE_PRIORITIES = {"low", "medium", "high"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NudgeAI MVP API",
        "canonical_backend": "simple_api_server.py",
        "nudge_store": str(NUDGE_STORE_PATH),
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        content = exc.detail
    else:
        content = {
            "error": {
                "code": "http_error",
                "message": str(exc.detail),
            }
        }
    return JSONResponse(status_code=exc.status_code, content=content)


class NudgeCreate(BaseModel):
    title: str = Field(..., min_length=1)
    context: Optional[str] = None
    dueAt: Optional[str] = None
    reminderAt: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title is required")
        return cleaned


class NudgePatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    context: Optional[str] = None
    dueAt: Optional[str] = None
    reminderAt: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["pending", "snoozed", "completed", "dismissed"]] = None
    snoozedUntil: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title cannot be blank")
        return cleaned


class CurrentLocationPatch(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracyMeters: Optional[float] = Field(None, ge=0)
    source: Literal["manual", "browser", "demo"] = "manual"
    label: Optional[str] = None


class CalendarStatusPatch(BaseModel):
    mode: Literal["manual", "demo", "unavailable", "error"] = "manual"
    freeForMinutes: int = Field(0, ge=0, le=1440)
    message: Optional[str] = None


class PlaceCreate(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radiusMeters: int = Field(300, gt=0, le=100000)
    tags: List[str] = []
    enabled: bool = True


class PlacePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radiusMeters: Optional[int] = Field(None, gt=0, le=100000)
    tags: Optional[List[str]] = None
    enabled: Optional[bool] = None


class ContextRuleCreate(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1)
    enabled: bool = True
    placeId: str
    requiredFreeMinutes: int = Field(45, ge=0, le=1440)
    timeWindow: Dict[str, str] = {"start": "06:00", "end": "22:00"}
    cooldownMinutes: int = Field(360, ge=0, le=43200)
    nudgeTemplate: Dict[str, str] = {
        "title": "Gym opportunity",
        "context": "You're near the gym and free for a bit. Go train?",
        "priority": "medium",
    }


class ContextRulePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    enabled: Optional[bool] = None
    placeId: Optional[str] = None
    requiredFreeMinutes: Optional[int] = Field(None, ge=0, le=1440)
    timeWindow: Optional[Dict[str, str]] = None
    cooldownMinutes: Optional[int] = Field(None, ge=0, le=43200)
    nudgeTemplate: Optional[Dict[str, str]] = None


class ExtractRequest(BaseModel):
    text_content: str = Field(..., min_length=1, max_length=20000)

    @field_validator("text_content")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text_content is required")
        return cleaned


class ExtractedSuggestion(BaseModel):
    title: str = Field(..., min_length=1)
    due_date: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=1)
    ai_note: str = ""

    @field_validator("title", "reasoning")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field cannot be blank")
        return cleaned

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_iso_or_empty(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        parsed = parse_datetime(value)
        return to_iso_z(parsed) if parsed else None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def to_iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_notification_state(nudge: Dict[str, Any]) -> Dict[str, Any]:
    if "last_notified_at" not in nudge:
        nudge["last_notified_at"] = None
    try:
        nudge["notification_count"] = int(nudge.get("notification_count") or 0)
    except (TypeError, ValueError):
        nudge["notification_count"] = 0
    return nudge


def reset_notification_state(nudge: Dict[str, Any]) -> None:
    nudge["last_notified_at"] = None
    nudge["notification_count"] = 0


ACTION_VERBS = [
    "apply",
    "ask",
    "book",
    "call",
    "check",
    "clean",
    "confirm",
    "email",
    "follow up",
    "message",
    "pay",
    "prepare",
    "print",
    "remind",
    "reply",
    "review",
    "schedule",
    "send",
    "submit",
    "update",
]

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def next_local_time(now: datetime, days: int, hour: int = 9, minute: int = 0) -> datetime:
    target = now.astimezone(timezone.utc) + timedelta(days=days)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


def add_business_days(now: datetime, days: int) -> datetime:
    current = now.astimezone(timezone.utc)
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current.replace(hour=9, minute=0, second=0, microsecond=0)


def next_weekday_datetime(now: datetime, weekday: int) -> datetime:
    current = now.astimezone(timezone.utc)
    days_ahead = (weekday - current.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return next_local_time(current, days_ahead)


def infer_due_date(text: str, now: Optional[datetime] = None) -> Optional[str]:
    now = now or datetime.now(timezone.utc)
    lower = text.lower()

    iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})(?:[tT ](\d{1,2}:\d{2}))?", text)
    if iso_match:
        date_text = iso_match.group(1)
        time_text = iso_match.group(2) or "09:00"
        parsed = parse_datetime(f"{date_text}T{time_text}:00Z")
        if parsed:
            return to_iso_z(parsed)

    business_match = re.search(r"\bin\s+(\d+)\s+business\s+days?\b", lower)
    if business_match:
        return to_iso_z(add_business_days(now, int(business_match.group(1))))

    days_match = re.search(r"\bin\s+(\d+)\s+days?\b", lower)
    if days_match:
        return to_iso_z(next_local_time(now, int(days_match.group(1))))

    if "tomorrow night" in lower or "tomorrow evening" in lower:
        return to_iso_z(next_local_time(now, 1, 20, 0))
    if "tomorrow" in lower:
        return to_iso_z(next_local_time(now, 1))
    if "tonight" in lower:
        return to_iso_z(next_local_time(now, 0, 20, 0))
    if "today" in lower:
        return to_iso_z(next_local_time(now, 0, 17, 0))
    if "next week" in lower:
        return to_iso_z(next_local_time(now, 7))

    weekday_match = re.search(r"\b(?:by|on|before|next)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lower)
    if weekday_match:
        return to_iso_z(next_weekday_datetime(now, WEEKDAYS[weekday_match.group(1)]))

    return None


def split_action_candidates(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    rough_parts = re.split(r"(?:\n|\.|;|\u2022|-\s)", normalized)
    candidates: List[str] = []
    for part in rough_parts:
        part = part.strip(" :-")
        if not part:
            continue
        pieces = re.split(r"\s+(?:and|then)\s+|,", part)
        candidates.extend(piece.strip(" :-") for piece in pieces if piece.strip(" :-"))
    return candidates


def clean_action_title(candidate: str) -> Optional[str]:
    lower = candidate.lower()
    verb_match = None
    for verb in ACTION_VERBS:
        match = re.search(rf"\b{re.escape(verb)}\b", lower)
        if match and (verb_match is None or match.start() < verb_match.start()):
            verb_match = match

    if not verb_match:
        return None

    title = candidate[verb_match.start():].strip(" .:-")
    title = re.sub(
        r"^(?:to\s+|please\s+|remember\s+to\s+|need\s+to\s+|needs\s+to\s+|i\s+should\s+|we\s+should\s+|she\s+said\s+to\s+|he\s+said\s+to\s+)",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip(" .:-")
    if len(title) < 3:
        return None
    title = title[:120].strip()
    return title[:1].upper() + title[1:]


def rule_based_extract(text_content: str, now: Optional[datetime] = None) -> List[ExtractedSuggestion]:
    now = now or datetime.now(timezone.utc)
    suggestions: List[ExtractedSuggestion] = []
    seen_titles = set()
    overall_due = infer_due_date(text_content, now)

    for candidate in split_action_candidates(text_content):
        title = clean_action_title(candidate)
        if not title:
            continue
        title_key = title.lower()
        if title_key in seen_titles:
            continue

        due_date = infer_due_date(candidate, now) or overall_due
        confidence = 0.72 if due_date else 0.58
        suggestions.append(
            ExtractedSuggestion(
                title=title,
                due_date=due_date,
                confidence_score=confidence,
                reasoning="Rule-based parser found an action verb and optional timing phrase in the provided text.",
                ai_note=candidate[:300],
            )
        )
        seen_titles.add(title_key)
        if len(suggestions) >= 8:
            break

    return suggestions


def extraction_prompt(text_content: str) -> str:
    return f"""You are NudgeAI's private extraction engine.

Privacy requirements:
- Process only this request.
- Do not store, train on, exfiltrate, or reveal the user's text.
- Return only structured JSON. Do not include markdown or commentary.

Extract reviewable nudge suggestions from the text. Do not save anything.

Return exactly this JSON shape:
{{
  "suggestions": [
    {{
      "title": "short action item",
      "due_date": "ISO-8601 UTC timestamp or null",
      "confidence_score": 0.0,
      "reasoning": "short reason grounded in the source text",
      "ai_note": "short source context"
    }}
  ]
}}

Resolve relative timing against the current UTC time {utc_now()}.
If the text has no actionable commitments, return {{"suggestions": []}}.

Text:
{text_content}
"""


def post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: float) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urlrequest.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    with urlrequest.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_llm_suggestions(content: str) -> List[ExtractedSuggestion]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    if not cleaned.startswith("{") and "{" in cleaned and "}" in cleaned:
        cleaned = cleaned[cleaned.find("{"): cleaned.rfind("}") + 1]

    payload = json.loads(cleaned)
    if isinstance(payload, dict):
        raw_suggestions = payload.get("suggestions", [])
    elif isinstance(payload, list):
        raw_suggestions = payload
    else:
        raw_suggestions = []
    if not isinstance(raw_suggestions, list):
        return []

    suggestions: List[ExtractedSuggestion] = []
    for item in raw_suggestions[:8]:
        if not isinstance(item, dict):
            continue
        try:
            suggestions.append(ExtractedSuggestion.model_validate(item))
        except ValueError:
            continue
    return suggestions


def call_local_extractor(prompt: str, timeout: float) -> Optional[List[ExtractedSuggestion]]:
    url = os.getenv("EXTRACT_LOCAL_LLM_URL")
    if not url:
        return None

    model = os.getenv("EXTRACT_LLM_MODEL", "llama3.1")
    if "/api/generate" in url:
        payload = {"model": model, "prompt": prompt, "stream": False, "format": "json"}
        response = post_json(url, payload, {}, timeout)
        content = response.get("response", "")
    else:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Return only valid JSON for NudgeAI extraction."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        response = post_json(url, payload, {}, timeout)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    return parse_llm_suggestions(content)


def call_external_extractor(provider: str, prompt: str, timeout: float) -> Optional[List[ExtractedSuggestion]]:
    allow_external = os.getenv("EXTRACT_ALLOW_EXTERNAL_LLM", "false").lower() == "true"
    if not allow_external:
        return None

    model = os.getenv("EXTRACT_LLM_MODEL")
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        model = model or "gpt-4o-mini"
    elif provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return None
        url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1/chat/completions")
        model = model or "mistral-small-latest"
    else:
        return None

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only valid JSON. Do not retain, train on, or disclose user data."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    response = post_json(url, payload, {"Authorization": f"Bearer {api_key}"}, timeout)
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    return parse_llm_suggestions(content)


def llm_extract(text_content: str) -> Optional[List[ExtractedSuggestion]]:
    provider = os.getenv("EXTRACT_LLM_PROVIDER", "auto").lower()
    if provider in {"rules", "rule", "disabled", "off"}:
        return None

    timeout = float(os.getenv("EXTRACT_LLM_TIMEOUT_SECONDS", "8"))
    prompt = extraction_prompt(text_content)
    try:
        if provider in {"auto", "local"}:
            local_result = call_local_extractor(prompt, timeout)
            if local_result is not None:
                return local_result
        if provider in {"openai", "mistral"}:
            return call_external_extractor(provider, prompt, timeout)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        logger.warning("LLM extraction unavailable; falling back to rules: %s", exc.__class__.__name__)
    return None


def extract_nudge_suggestions(text_content: str) -> Dict[str, Any]:
    llm_suggestions = llm_extract(text_content)
    if llm_suggestions is not None:
        return {"suggestions": llm_suggestions, "source": "llm"}
    return {"suggestions": rule_based_extract(text_content), "source": "rules"}


def load_nudges() -> List[Dict[str, Any]]:
    if not NUDGE_STORE_PATH.exists():
        return []
    try:
        data = json.loads(NUDGE_STORE_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            logger.error("Nudge store is not a list; ignoring invalid store")
            return []
        return [ensure_notification_state(item) for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        logger.error("Nudge store contains invalid JSON")
        return []


def save_nudges(nudges: List[Dict[str, Any]]) -> None:
    NUDGE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NUDGE_STORE_PATH.write_text(json.dumps(nudges, indent=2), encoding="utf-8")


def create_nudge_record(
    title: str,
    context: Optional[str] = None,
    due_at: Optional[str] = None,
    reminder_at: Optional[str] = None,
    priority: str = "medium",
    source: str = "manual",
) -> Dict[str, Any]:
    now = utc_now()
    return {
        "id": str(uuid4()),
        "title": title,
        "context": context,
        "dueAt": due_at,
        "reminderAt": reminder_at,
        "snoozedUntil": None,
        "status": "pending",
        "priority": priority,
        "source": source,
        "createdAt": now,
        "updatedAt": now,
        "completedAt": None,
        "last_notified_at": None,
        "notification_count": 0,
    }


def find_nudge(nudge_id: str, nudges: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return next((nudge for nudge in nudges if nudge.get("id") == nudge_id), None)


def demo_places() -> List[Dict[str, Any]]:
    return [
        {
            "id": "gym-demo",
            "name": "Gym",
            "latitude": -33.8688,
            "longitude": 151.2093,
            "radiusMeters": 300,
            "tags": ["fitness", "personal"],
            "enabled": True,
        }
    ]


def demo_context_rules() -> List[Dict[str, Any]]:
    return [
        {
            "id": "gym-opportunity",
            "name": "Gym Opportunity",
            "enabled": True,
            "placeId": "gym-demo",
            "requiredFreeMinutes": 45,
            "timeWindow": {"start": "06:00", "end": "22:00"},
            "cooldownMinutes": 360,
            "nudgeTemplate": {
                "title": "Gym opportunity",
                "context": "You're near the gym and free for a bit. Go train?",
                "priority": "medium",
            },
        }
    ]


def demo_current_location() -> Dict[str, Any]:
    return {
        "latitude": -33.8688,
        "longitude": 151.2093,
        "accuracyMeters": 30,
        "source": "demo",
        "label": "Demo gym location",
        "updatedAt": utc_now(),
    }


def demo_calendar_availability() -> Dict[str, Any]:
    return {
        "mode": "demo",
        "freeForMinutes": 60,
        "message": "Using demo calendar availability.",
        "updatedAt": utc_now(),
    }


def load_json_store(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, type(default)) else default
    except json.JSONDecodeError:
        logger.error("Invalid JSON in %s; using demo defaults", path)
        return default


def save_json_store(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_places() -> List[Dict[str, Any]]:
    return load_json_store(PLACES_STORE_PATH, demo_places())


def save_places(places: List[Dict[str, Any]]) -> None:
    save_json_store(PLACES_STORE_PATH, places)


def load_context_rules() -> List[Dict[str, Any]]:
    return load_json_store(CONTEXT_RULES_STORE_PATH, demo_context_rules())


def save_context_rules(rules: List[Dict[str, Any]]) -> None:
    save_json_store(CONTEXT_RULES_STORE_PATH, rules)


def load_rule_state() -> List[Dict[str, Any]]:
    return load_json_store(RULE_STATE_STORE_PATH, [])


def save_rule_state(rule_state: List[Dict[str, Any]]) -> None:
    save_json_store(RULE_STATE_STORE_PATH, rule_state)


def load_current_location() -> Optional[Dict[str, Any]]:
    return load_json_store(CURRENT_LOCATION_STORE_PATH, demo_current_location())


def save_current_location(location: Dict[str, Any]) -> None:
    save_json_store(CURRENT_LOCATION_STORE_PATH, location)


def load_calendar_availability() -> Dict[str, Any]:
    return load_json_store(CALENDAR_AVAILABILITY_STORE_PATH, demo_calendar_availability())


def save_calendar_availability(calendar: Dict[str, Any]) -> None:
    save_json_store(CALENDAR_AVAILABILITY_STORE_PATH, calendar)


def load_context_state() -> Dict[str, Any]:
    return {
        "places": load_places(),
        "rules": load_context_rules(),
        "ruleState": load_rule_state(),
        "currentLocation": load_current_location(),
        "calendar": load_calendar_availability(),
    }


def save_context_state(state: Dict[str, Any]) -> None:
    save_places(state.get("places", demo_places()))
    save_context_rules(state.get("rules", demo_context_rules()))
    save_rule_state(state.get("ruleState", []))
    if state.get("currentLocation"):
        save_current_location(state["currentLocation"])
    save_calendar_availability(state.get("calendar", demo_calendar_availability()))


def distance_meters(origin: Dict[str, Any], destination: Dict[str, Any]) -> float:
    lat1 = math.radians(float(origin["latitude"]))
    lon1 = math.radians(float(origin["longitude"]))
    lat2 = math.radians(float(destination["latitude"]))
    lon2 = math.radians(float(destination["longitude"]))
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    haversine = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 6371000 * 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))


def context_source_status(state: Dict[str, Any]) -> Dict[str, Any]:
    location = state.get("currentLocation")
    calendar = state.get("calendar", {})
    location_source = location.get("source", "manual") if location else "missing"
    calendar_mode = calendar.get("mode", "unavailable")
    return {
        "location": {
            "status": location_source if location else "missing",
            "message": {
                "demo": "Using demo location.",
                "manual": "Manual location set.",
                "browser": "Browser location set while the app is open.",
                "missing": "No location source configured.",
            }.get(location_source, "Location source unavailable."),
            "updatedAt": location.get("updatedAt") if location else None,
        },
        "calendar": {
            "status": calendar_mode,
            "message": calendar.get("message") or {
                "demo": "Using demo calendar availability.",
                "manual": "Using manual calendar availability.",
                "unavailable": "Calendar unavailable; using demo/free fallback.",
                "error": "Calendar availability failed to load.",
            }.get(calendar_mode, "Calendar availability unavailable."),
            "freeForMinutes": calendar.get("freeForMinutes", 0),
            "updatedAt": calendar.get("updatedAt"),
        },
    }


def parse_hhmm(value: str) -> int:
    hour_text, minute_text = value.split(":", 1)
    hour = int(hour_text)
    minute = int(minute_text)
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("time must be HH:MM")
    return hour * 60 + minute


def is_inside_time_window(now: datetime, time_window: Dict[str, str]) -> bool:
    start = parse_hhmm(time_window.get("start", "06:00"))
    end = parse_hhmm(time_window.get("end", "22:00"))
    current = now.hour * 60 + now.minute
    if start > end:
        # Overnight windows are intentionally deferred for this local MVP.
        return False
    return start <= current <= end


def is_calendar_free(required_free_minutes: int, calendar: Dict[str, Any], now: datetime) -> bool:
    _ = now
    return int(calendar.get("freeForMinutes", 0)) >= required_free_minutes


def find_rule_state(rule_state: List[Dict[str, Any]], rule_id: str) -> Optional[Dict[str, Any]]:
    return next((item for item in rule_state if item.get("ruleId") == rule_id), None)


def is_cooldown_clear(rule: Dict[str, Any], rule_state: List[Dict[str, Any]], now: datetime) -> bool:
    state = find_rule_state(rule_state, rule["id"])
    last_fired = parse_datetime((state or {}).get("lastFiredAt"))
    if not last_fired:
        return True
    elapsed_minutes = (now.astimezone(timezone.utc) - last_fired).total_seconds() / 60
    return elapsed_minutes >= int(rule.get("cooldownMinutes", 0))


def set_rule_last_fired(rule_state: List[Dict[str, Any]], rule_id: str, fired_at: str) -> List[Dict[str, Any]]:
    state = find_rule_state(rule_state, rule_id)
    if state:
        state["lastFiredAt"] = fired_at
        return rule_state
    return [*rule_state, {"ruleId": rule_id, "lastFiredAt": fired_at}]


def evaluate_context_rule(
    rule: Dict[str, Any],
    places: List[Dict[str, Any]],
    current_location: Optional[Dict[str, Any]],
    calendar: Dict[str, Any],
    rule_state: List[Dict[str, Any]],
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    now = now or datetime.now().astimezone()
    place = next((item for item in places if item.get("id") == rule.get("placeId")), None)
    reasons: List[str] = []

    if not rule.get("enabled"):
        reasons.append("Rule is disabled.")
    if not place or not place.get("enabled"):
        reasons.append("Place is not configured or disabled.")
    if not current_location:
        reasons.append("Current location is not set.")

    distance = None
    if place and current_location:
        distance = distance_meters(current_location, place)
        if distance > float(place.get("radiusMeters", 0)):
            reasons.append(f"Current location is {round(distance)}m from {place.get('name')}, outside the {place.get('radiusMeters')}m radius.")

    required_free = int(rule.get("requiredFreeMinutes", 45))
    if not is_calendar_free(required_free, calendar, now):
        reasons.append(f"Calendar is free for {int(calendar.get('freeForMinutes', 0))} minutes, less than required {required_free} minutes.")

    if not is_inside_time_window(now, rule.get("timeWindow", {})):
        window = rule.get("timeWindow", {})
        reasons.append(f"Current local time is outside {window.get('start', '06:00')}-{window.get('end', '22:00')}.")

    if not is_cooldown_clear(rule, rule_state, now):
        reasons.append("Rule cooldown is still active.")

    matched = len(reasons) == 0
    return {
        "ruleId": rule.get("id"),
        "ruleName": rule.get("name"),
        "matched": matched,
        "distanceMeters": round(distance) if distance is not None else None,
        "reasons": reasons,
        "message": f"{rule.get('name')} matched." if matched else f"{rule.get('name')} did not match.",
    }


def evaluate_all_context_rules(now: Optional[datetime] = None, create_nudges: bool = True) -> Dict[str, Any]:
    now = now or datetime.now().astimezone()
    state = load_context_state()
    evaluations = []
    created_nudges = []
    rule_state = state["ruleState"]

    for rule in state["rules"]:
        result = evaluate_context_rule(
            rule,
            state["places"],
            state["currentLocation"],
            state["calendar"],
            rule_state,
            now,
        )
        if result["matched"] and create_nudges:
            template = rule.get("nudgeTemplate", {})
            rule_context = template.get("context", "")
            nudge = create_nudge_record(
                title=template.get("title", rule.get("name", "Context nudge")),
                context=f"{rule.get('name')}: {rule_context}",
                priority=template.get("priority", "medium"),
                source="context_rule",
            )
            nudges = load_nudges()
            nudges.append(nudge)
            save_nudges(nudges)
            rule_state = set_rule_last_fired(rule_state, rule["id"], utc_now())
            result["createdNudgeId"] = nudge["id"]
            created_nudges.append(nudge)
        evaluations.append(result)

    state["ruleState"] = rule_state
    save_rule_state(rule_state)
    return {
        "created": bool(created_nudges),
        "nudges": created_nudges,
        "nudge": created_nudges[0] if created_nudges else None,
        "evaluations": evaluations,
        "sourceStatus": context_source_status(state),
    }


def matches_due_today(nudge: Dict[str, Any], now: datetime) -> bool:
    due_at = parse_datetime(nudge.get("dueAt"))
    return bool(due_at and due_at.date() == now.date())


def matches_overdue(nudge: Dict[str, Any], now: datetime) -> bool:
    due_at = parse_datetime(nudge.get("dueAt"))
    return bool(
        due_at
        and due_at < now
        and nudge.get("status") not in {"completed", "dismissed"}
    )


def is_notification_active(nudge: Dict[str, Any], now: datetime) -> bool:
    status = nudge.get("status", "pending")
    if status in {"completed", "dismissed"}:
        return False
    if status == "snoozed":
        snoozed_until = parse_datetime(nudge.get("snoozedUntil"))
        return bool(snoozed_until and snoozed_until <= now)
    return status == "pending"


def already_notified(nudge: Dict[str, Any]) -> bool:
    ensure_notification_state(nudge)
    return bool(nudge.get("last_notified_at") or nudge.get("notification_count", 0) > 0)


def context_rule_recently_created(nudge: Dict[str, Any], now: datetime) -> bool:
    created_at = parse_datetime(nudge.get("createdAt"))
    if not created_at:
        return False
    return now - created_at <= timedelta(hours=24)


def build_notification_alert(nudge: Dict[str, Any], now: datetime) -> Optional[Dict[str, str]]:
    ensure_notification_state(nudge)
    if already_notified(nudge) or not is_notification_active(nudge, now):
        return None

    if nudge.get("source") == "context_rule" and context_rule_recently_created(nudge, now):
        return {
            "id": nudge.get("id", ""),
            "title": nudge.get("title", "Context nudge"),
            "body": nudge.get("context") or "A local context rule created a nudge.",
            "type": "context_rule",
        }

    due_at = parse_datetime(nudge.get("dueAt"))
    if due_at and due_at.date() <= now.date():
        timing = "Overdue" if due_at < now else "Due today"
        return {
            "id": nudge.get("id", ""),
            "title": nudge.get("title", "Nudge due"),
            "body": f"{timing}: {nudge.get('context') or 'Open NudgeAI to review this nudge.'}",
            "type": "due_today",
        }

    return None


def poll_notification_alerts(now: Optional[datetime] = None) -> List[Dict[str, str]]:
    now = now or datetime.now(timezone.utc)
    notified_at = to_iso_z(now)
    nudges = load_nudges()
    alerts: List[Dict[str, str]] = []

    for nudge in nudges:
        alert = build_notification_alert(nudge, now)
        if not alert:
            continue
        alerts.append(alert)
        nudge["last_notified_at"] = notified_at
        nudge["notification_count"] = int(nudge.get("notification_count") or 0) + 1

    if alerts:
        save_nudges(nudges)
    return alerts


@app.get("/api/nudges")
async def list_nudges(
    status: Optional[Literal["pending", "snoozed", "completed", "dismissed"]] = None,
    priority: Optional[Literal["low", "medium", "high"]] = None,
    dueToday: bool = Query(False),
    overdue: bool = Query(False),
):
    """Return persisted local MVP nudges with optional filters."""
    nudges = load_nudges()
    now = datetime.now(timezone.utc)

    if status:
        nudges = [nudge for nudge in nudges if nudge.get("status") == status]
    if priority:
        nudges = [nudge for nudge in nudges if nudge.get("priority") == priority]
    if dueToday:
        nudges = [nudge for nudge in nudges if matches_due_today(nudge, now)]
    if overdue:
        nudges = [nudge for nudge in nudges if matches_overdue(nudge, now)]

    nudges.sort(key=lambda item: (item.get("dueAt") or "9999", item.get("createdAt") or ""))
    return {"nudges": nudges, "count": len(nudges)}


@app.post("/api/nudges", status_code=201)
async def create_nudge(payload: NudgeCreate):
    """Create a manual nudge."""
    nudge = create_nudge_record(
        title=payload.title,
        context=payload.context,
        due_at=payload.dueAt,
        reminder_at=payload.reminderAt,
        priority=payload.priority,
    )
    nudges = load_nudges()
    nudges.append(nudge)
    save_nudges(nudges)
    return {"nudge": nudge}


@app.post("/api/extract")
async def extract_nudges(payload: ExtractRequest):
    """Extract review-only nudge suggestions from messy text without saving them."""
    result = extract_nudge_suggestions(payload.text_content)
    suggestions = [suggestion.model_dump() for suggestion in result["suggestions"]]
    return {
        "suggestions": suggestions,
        "count": len(suggestions),
        "source": result["source"],
    }


@app.get("/api/notifications/poll")
async def poll_notifications():
    """Return immediate local alert payloads and mark them notified."""
    return poll_notification_alerts()


@app.get("/api/context")
async def get_context_state():
    """Return local personal context rule configuration and source status."""
    state = load_context_state()
    return {
        "places": state["places"],
        "rules": state["rules"],
        "ruleState": state["ruleState"],
        "currentLocation": state["currentLocation"],
        "calendar": state["calendar"],
        "sourceStatus": context_source_status(state),
    }


@app.get("/api/source-status")
async def get_source_status():
    """Return local source status cards for personal context rules."""
    return {"sourceStatus": context_source_status(load_context_state())}


@app.get("/api/places")
async def get_places():
    """Return local/demo places used by context rules."""
    return {"places": load_places()}


@app.post("/api/places", status_code=201)
async def create_place(payload: PlaceCreate):
    """Create a local place. Private real coordinates are stored in ignored local files."""
    places = load_places()
    place = {
        "id": payload.id or str(uuid4()),
        "name": payload.name.strip(),
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "radiusMeters": payload.radiusMeters,
        "tags": payload.tags,
        "enabled": payload.enabled,
    }
    places.append(place)
    save_places(places)
    return {"place": place}


def update_place_record(place_id: str, payload: PlacePatch) -> Dict[str, Any]:
    places = load_places()
    place = next((item for item in places if item.get("id") == place_id), None)
    if not place:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "not_found", "message": "Place not found."}},
        )

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and isinstance(updates["name"], str):
        updates["name"] = updates["name"].strip()

    for field_name, value in updates.items():
        place[field_name] = value

    save_places(places)
    return place


@app.patch("/api/places/{place_id}")
async def patch_place(place_id: str, payload: PlacePatch):
    """Update a local place used by context rules."""
    return {"place": update_place_record(place_id, payload)}


@app.put("/api/places/{place_id}")
async def put_place(place_id: str, payload: PlacePatch):
    """Replace mutable local place fields used by context rules."""
    return {"place": update_place_record(place_id, payload)}


@app.get("/api/context-rules")
async def get_context_rules():
    """Return local/demo context rules."""
    return {"rules": load_context_rules(), "ruleState": load_rule_state()}


@app.post("/api/context-rules", status_code=201)
async def create_context_rule(payload: ContextRuleCreate):
    """Create a local context rule."""
    rules = load_context_rules()
    rule = {
        "id": payload.id or str(uuid4()),
        "name": payload.name.strip(),
        "enabled": payload.enabled,
        "placeId": payload.placeId,
        "requiredFreeMinutes": payload.requiredFreeMinutes,
        "timeWindow": payload.timeWindow,
        "cooldownMinutes": payload.cooldownMinutes,
        "nudgeTemplate": payload.nudgeTemplate,
    }
    rules.append(rule)
    save_context_rules(rules)
    return {"rule": rule}


def update_context_rule_record(rule_id: str, payload: ContextRulePatch) -> Dict[str, Any]:
    rules = load_context_rules()
    rule = next((item for item in rules if item.get("id") == rule_id), None)
    if not rule:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "not_found", "message": "Context rule not found."}},
        )

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and isinstance(updates["name"], str):
        updates["name"] = updates["name"].strip()

    for field_name, value in updates.items():
        rule[field_name] = value

    save_context_rules(rules)
    return rule


@app.patch("/api/context-rules/{rule_id}")
async def patch_context_rule(rule_id: str, payload: ContextRulePatch):
    """Update a local context rule."""
    return {"rule": update_context_rule_record(rule_id, payload)}


@app.put("/api/context-rules/{rule_id}")
async def put_context_rule(rule_id: str, payload: ContextRulePatch):
    """Replace mutable local context rule fields."""
    return {"rule": update_context_rule_record(rule_id, payload)}


@app.get("/api/current-location")
async def get_current_location():
    """Return the manual/demo current location source."""
    return {"currentLocation": load_current_location()}


@app.post("/api/current-location")
async def set_current_location(payload: CurrentLocationPatch):
    """Set the manual current location used by local context rules."""
    location = {
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "accuracyMeters": payload.accuracyMeters,
        "source": payload.source,
        "label": payload.label or "Manual location",
        "updatedAt": utc_now(),
    }
    save_current_location(location)
    state = load_context_state()
    return {"currentLocation": location, "sourceStatus": context_source_status(state)}


@app.patch("/api/context/location")
async def update_current_location(payload: CurrentLocationPatch):
    """Set the manual current location used by local context rules."""
    return await set_current_location(payload)


@app.patch("/api/context/calendar")
async def update_calendar_status(payload: CalendarStatusPatch):
    """Set the manual calendar free/busy state used by local context rules."""
    calendar = {
        "mode": payload.mode,
        "freeForMinutes": payload.freeForMinutes,
        "message": payload.message or f"Manual calendar availability: free for {payload.freeForMinutes} minutes.",
        "updatedAt": utc_now(),
    }
    save_calendar_availability(calendar)
    return {"calendar": calendar, "sourceStatus": context_source_status(load_context_state())}


@app.post("/api/context-rules/evaluate")
async def evaluate_context_rules_v2():
    """Evaluate local context rules and create normal nudges when they match."""
    return evaluate_all_context_rules()


@app.post("/api/context/evaluate")
async def evaluate_context_rules():
    """Evaluate local context rules and create a normal nudge when one matches."""
    return evaluate_all_context_rules()


@app.patch("/api/nudges/{nudge_id}")
async def update_nudge(nudge_id: str, payload: NudgePatch):
    """Update mutable nudge fields and status."""
    nudges = load_nudges()
    nudge = find_nudge(nudge_id, nudges)
    if not nudge:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "not_found", "message": "Nudge not found."}},
        )

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        nudge[field_name] = value

    if "status" in updates:
        if updates["status"] == "completed":
            nudge["completedAt"] = utc_now()
        elif nudge.get("status") != "completed":
            # Reopening or dismissing a completed nudge clears the completion time.
            nudge["completedAt"] = None

    if {"status", "dueAt", "reminderAt", "snoozedUntil"}.intersection(updates):
        reset_notification_state(nudge)

    nudge["updatedAt"] = utc_now()
    save_nudges(nudges)
    return {"nudge": nudge}


@app.delete("/api/nudges/{nudge_id}")
async def delete_nudge(nudge_id: str):
    """Hard delete a local MVP nudge."""
    nudges = load_nudges()
    remaining = [nudge for nudge in nudges if nudge.get("id") != nudge_id]
    if len(remaining) == len(nudges):
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "not_found", "message": "Nudge not found."}},
        )
    save_nudges(remaining)
    return {"deleted": True, "id": nudge_id}


def safe_load_json_file(filename):
    """Safely load JSON file with error handling"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File {filename} not found")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {filename}")
        return []
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return []


@app.get("/api/mcp/tools/query_calendar")
async def get_calendar_events(start_date: str = None, end_date: str = None):
    """Get calendar events from the system with optional date filtering"""
    try:
        # Load calendar events from the generated file
        calendar_data = safe_load_json_file("calendar_events.json")

        if isinstance(calendar_data, list) and len(calendar_data) > 0:
            formatted_events = []
            for event in calendar_data:  # Get all events, not just first 10
                if isinstance(event, dict):
                    # Extract relevant fields from Google Calendar API format
                    start_info = event.get("start", {})
                    start_time = start_info.get(
                        "dateTime", start_info.get("date", "N/A")
                    )
                    
                    # Also extract end time if available
                    end_info = event.get("end", {})
                    end_time = end_info.get(
                        "dateTime", end_info.get("date", "")
                    )

                    formatted_event = {
                        "id": event.get("id", ""),
                        "summary": event.get("summary", "Event"),
                        "title": event.get("summary", "Event"),  # For compatibility with frontend
                        "start_time": start_time,
                        "end_time": end_time,
                        "type": event.get("eventType", "event"),
                        "description": event.get("description", ""),
                        "location": event.get("location", ""),
                        "attendees": [attendee.get("email", "") for attendee in event.get("attendees", [])],
                    }

                    # Apply date filtering if dates are provided
                    if start_date and end_date:
                        # Check if event is within the date range
                        if start_time != "N/A" and start_time >= start_date and start_time <= end_date:
                            formatted_events.append(formatted_event)
                    else:
                        # If no date filters, include all events
                        formatted_events.append(formatted_event)

            return {"result": {"events": formatted_events}}

        # Fallback to known events
        return {
            "result": {
                "events": [
                    {
                        "id": "hackathon-event",
                        "title": "Mistral Worldwide Hackathon - Sydney edition",
                        "summary": "Mistral Worldwide Hackathon - Sydney edition",
                        "start_time": "2026-02-28T09:00:00+11:00",
                        "end_time": "2026-02-28T17:00:00+11:00",
                        "type": "event",
                        "description": "Major hackathon event at Michael Crouch Innovation Centre, Sydney",
                        "location": "Michael Crouch Innovation Centre, Sydney",
                        "attendees": ["organizers@mistral.com", "participants@sydney.edu.au"]
                    },
                    {
                        "id": "wake-up-list",
                        "title": "WAKE UP LIST",
                        "summary": "WAKE UP LIST",
                        "start_time": "2026-03-01T09:00:00+11:00",
                        "end_time": "2026-03-01T09:30:00+11:00",
                        "type": "reminder",
                        "description": "Daily routine tasks to start the day",
                        "location": "Home",
                        "attendees": []
                    },
                    {
                        "id": "meeting-with-manoj",
                        "title": "Meeting with Manoj",
                        "summary": "Meeting with Manoj",
                        "start_time": "2026-03-02T22:00:00+11:00",
                        "end_time": "2026-03-02T23:00:00+11:00",
                        "type": "meeting",
                        "description": "Project discussion and planning",
                        "location": "Online",
                        "attendees": ["manoj@example.com", "me@example.com"]
                    },
                    {
                        "id": "atlassian-takeover",
                        "title": "Atlassian Takeover 2026",
                        "summary": "Atlassian Takeover 2026",
                        "start_time": "2026-03-03T18:00:00+11:00",
                        "end_time": "2026-03-03T20:00:00+11:00",
                        "type": "event",
                        "description": "Special event for Atlassian community",
                        "location": "Sydney CBD",
                        "attendees": ["community@atlassian.com", "attendees@event.com"]
                    }
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in get_calendar_events: {e}")
        return {
            "result": {
                "events": [
                    {
                        "id": "hackathon-event",
                        "title": "Mistral Worldwide Hackathon - Sydney edition",
                        "summary": "Mistral Worldwide Hackathon - Sydney edition",
                        "start_time": "2026-02-28T09:00:00+11:00",
                        "end_time": "2026-02-28T17:00:00+11:00",
                        "type": "event",
                        "description": "Major hackathon event at Michael Crouch Innovation Centre, Sydney",
                        "location": "Michael Crouch Innovation Centre, Sydney",
                        "attendees": ["organizers@mistral.com", "participants@sydney.edu.au"]
                    },
                    {
                        "id": "wake-up-list",
                        "title": "WAKE UP LIST",
                        "summary": "WAKE UP LIST",
                        "start_time": "2026-03-01T09:00:00+11:00",
                        "end_time": "2026-03-01T09:30:00+11:00",
                        "type": "reminder",
                        "description": "Daily routine tasks to start the day",
                        "location": "Home",
                        "attendees": []
                    },
                    {
                        "id": "meeting-with-manoj",
                        "title": "Meeting with Manoj",
                        "summary": "Meeting with Manoj",
                        "start_time": "2026-03-02T22:00:00+11:00",
                        "end_time": "2026-03-02T23:00:00+11:00",
                        "type": "meeting",
                        "description": "Project discussion and planning",
                        "location": "Online",
                        "attendees": ["manoj@example.com", "me@example.com"]
                    },
                    {
                        "id": "atlassian-takeover",
                        "title": "Atlassian Takeover 2026",
                        "summary": "Atlassian Takeover 2026",
                        "start_time": "2026-03-03T18:00:00+11:00",
                        "end_time": "2026-03-03T20:00:00+11:00",
                        "type": "event",
                        "description": "Special event for Atlassian community",
                        "location": "Sydney CBD",
                        "attendees": ["community@atlassian.com", "attendees@event.com"]
                    }
                ]
            }
        }
@app.get("/api/mcp/tools/query_drive")
async def search_documents():
    """Get documents from the system"""
    try:
        # Try to load from potential document files
        doc_data = safe_load_json_file("drive_documents.json")

        if isinstance(doc_data, list) and len(doc_data) > 0:
            formatted_docs = []
            for doc in doc_data:
                if isinstance(doc, dict):
                    formatted_doc = {
                        "title": doc.get("name", doc.get("title", "Untitled Document")),
                        "url": doc.get("webViewLink", doc.get("url", "#")),
                        "modified": doc.get("modifiedTime", "Unknown"),
                        "type": doc.get("mimeType", "document"),
                        "id": doc.get("id", ""),
                    }
                    formatted_docs.append(formatted_doc)

            if formatted_docs:
                return {"result": {"documents": formatted_docs}}

        # Fallback to known documents
        return {
            "result": {
                "documents": [
                    {
                        "title": "Marketing Budget 2024.xlsx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-27T14:30:00Z",
                        "type": "spreadsheet",
                        "id": "budget-sheet",
                    },
                    {
                        "title": "Project Plan.docx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-26T10:15:00Z",
                        "type": "document",
                        "id": "project-plan",
                    },
                    {
                        "title": "Meeting Notes.pdf",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-25T16:45:00Z",
                        "type": "pdf",
                        "id": "meeting-notes",
                    },
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in search_documents: {e}")
        return {
            "result": {
                "documents": [
                    {
                        "title": "Marketing Budget 2024.xlsx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-27T14:30:00Z",
                        "type": "spreadsheet",
                        "id": "budget-sheet",
                    },
                    {
                        "title": "Project Plan.docx",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-26T10:15:00Z",
                        "type": "document",
                        "id": "project-plan",
                    },
                    {
                        "title": "Meeting Notes.pdf",
                        "url": "https://drive.google.com/file/d/...",
                        "modified": "2026-02-25T16:45:00Z",
                        "type": "pdf",
                        "id": "meeting-notes",
                    },
                ]
            }
        }


@app.get("/api/mcp/tools/query_location")
async def get_location_history():
    """Get location history from the system"""
    try:
        # Load location data
        location_data = safe_load_json_file("location_history.json")

        if isinstance(location_data, list) and len(location_data) > 0:
            formatted_locations = []
            for loc in location_data[:10]:
                if isinstance(loc, dict):
                    formatted_loc = {
                        "place": loc.get(
                            "place_name", loc.get("place", "Unknown Location")
                        ),
                        "time": loc.get("timestamp", "Unknown"),
                        "duration": loc.get("duration", "Unknown"),
                        "type": loc.get("location_type", "location"),
                        "coordinates": {
                            "lat": loc.get("latitude", 0),
                            "lng": loc.get("longitude", 0),
                        },
                        "id": loc.get("id", ""),
                    }
                    formatted_locations.append(formatted_loc)

            if formatted_locations:
                return {"result": {"locations": formatted_locations}}

        # Fallback to known locations
        return {
            "result": {
                "locations": [
                    {
                        "place": "Home",
                        "time": "2026-02-28T08:00:00+11:00",
                        "duration": "16h",
                        "type": "home",
                        "coordinates": {"lat": -33.8688, "lng": 151.2093},
                        "id": "home-location",
                    },
                    {
                        "place": "Office",
                        "time": "2026-02-28T09:00:00+11:00",
                        "duration": "9h",
                        "type": "work",
                        "coordinates": {"lat": -33.8651, "lng": 151.2099},
                        "id": "office-location",
                    },
                    {
                        "place": "Gym",
                        "time": "2026-02-28T18:30:00+11:00",
                        "duration": "1h",
                        "type": "exercise",
                        "coordinates": {"lat": -33.8702, "lng": 151.2089},
                        "id": "gym-location",
                    },
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error in get_location_history: {e}")
        return {
            "result": {
                "locations": [
                    {
                        "place": "Home",
                        "time": "2026-02-28T08:00:00+11:00",
                        "duration": "16h",
                        "type": "home",
                        "coordinates": {"lat": -33.8688, "lng": 151.2093},
                        "id": "home-location",
                    },
                    {
                        "place": "Office",
                        "time": "2026-02-28T09:00:00+11:00",
                        "duration": "9h",
                        "type": "work",
                        "coordinates": {"lat": -33.8651, "lng": 151.2099},
                        "id": "office-location",
                    },
                    {
                        "place": "Gym",
                        "time": "2026-02-28T18:30:00+11:00",
                        "duration": "1h",
                        "type": "exercise",
                        "coordinates": {"lat": -33.8702, "lng": 151.2089},
                        "id": "gym-location",
                    },
                ]
            }
        }


@app.get("/api/mcp/tools/query_fit")
async def get_health_data():
    """Get health/fitness data from the system"""
    try:
        # Load fitness data
        fit_data = safe_load_json_file("fit_data.json")

        if isinstance(fit_data, list) and len(fit_data) > 0:
            # Calculate summary statistics
            total_steps = sum(
                [item.get("steps", 0) for item in fit_data if isinstance(item, dict)]
            )
            total_calories = sum(
                [item.get("calories", 0) for item in fit_data if isinstance(item, dict)]
            )
            total_duration = sum(
                [
                    item.get("duration_minutes", 0)
                    for item in fit_data
                    if isinstance(item, dict)
                ]
            )

            recent_activities = []
            for activity in fit_data[:5]:
                if isinstance(activity, dict):
                    recent_activities.append(
                        {
                            "type": activity.get("activity_type", "unknown"),
                            "duration": activity.get("duration_minutes", 0),
                            "steps": activity.get("steps", 0),
                            "calories": activity.get("calories", 0),
                            "timestamp": activity.get("timestamp", "N/A"),
                        }
                    )

            return {
                "result": {
                    "health": {
                        "steps_today": total_steps,
                        "calories_burned": total_calories,
                        "active_minutes": total_duration,
                        "recent_activities": recent_activities,
                    }
                }
            }

        # Fallback to sample data
        return {
            "result": {
                "health": {
                    "steps_today": 8547,
                    "calories_burned": 2100,
                    "active_minutes": 65,
                    "heart_rate_avg": 72,
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in get_health_data: {e}")
        return {
            "result": {
                "health": {
                    "steps_today": 8547,
                    "calories_burned": 2100,
                    "active_minutes": 65,
                    "heart_rate_avg": 72,
                }
            }
        }



@app.get("/api/mcp/tools/semantic_search")
async def semantic_search(query: str, k: int = 5):
    """Perform semantic search across all indexed data"""
    try:
        # For now, return a mock response - in a real implementation, this would connect to the RAG system
        logger.info(f"Semantic search requested for query: '{query}', k={k}")
        
        # Mock response showing what the semantic search would return
        mock_results = [
            {
                "document_id": "event_1",
                "metadata": {
                    "title": "Atlassian Takeover 2026",
                    "type": "calendar_event",
                    "summary": "Atlassian community event",
                    "start_time": "2026-03-03T18:00:00+11:00",
                    "location": "Level 6, 341 George St, Sydney, au",
                    "description": "Atlassian are continuing their association with SydJS for another superb year..."
                },
                "similarity_score": 0.92,
                "relevance_explanation": "This event matches your query about Atlassian events"
            },
            {
                "document_id": "event_2", 
                "metadata": {
                    "title": "Meeting with Manoj",
                    "type": "calendar_event",
                    "summary": "Project discussion",
                    "start_time": "2026-03-02T22:00:00+11:00",
                    "location": "Online",
                    "description": "Project discussion and planning"
                },
                "similarity_score": 0.85,
                "relevance_explanation": "This meeting involves project discussions relevant to your query"
            },
            {
                "document_id": "event_3",
                "metadata": {
                    "title": "Mistral Worldwide Hackathon - Sydney edition", 
                    "type": "calendar_event",
                    "summary": "Major hackathon event",
                    "start_time": "2026-02-28T09:00:00+11:00",
                    "location": "Michael Crouch Innovation Centre, Level G...",
                    "description": "Get up-to-date information at: https://luma.com/event/evt-5HpmRJyi64mzcvA?pk=g-H2hK7KXBsq5jyDx"
                },
                "similarity_score": 0.78,
                "relevance_explanation": "This major event might be relevant to your interests"
            }
        ]
        
        return {
            "query": query,
            "results": mock_results[:k],  # Limit to k results
            "total_found": len(mock_results),
            "search_performed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in semantic_search: {e}")
        return {
            "query": query,
            "results": [],
            "total_found": 0,
            "search_performed_at": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
