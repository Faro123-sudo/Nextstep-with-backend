"""
Thread-safe read/write helpers for the frontend careerData.json file.

When the AI generates a new career entry that didn't exist in the static
JSON, we append it so future searches hit the file directly without
consuming Gemini tokens.
"""

import json
import os
import threading
from pathlib import Path
from typing import Optional

# Path to the frontend's static career data JSON
_CAREER_JSON_PATH = Path(__file__).resolve().parent.parent.parent / "Nextstep-frontend" / "nextstep-navigator" / "src" / "data" / "careerData.json"

_lock = threading.Lock()


def _read_json() -> dict:
    """Read the full careerData.json as a dict.  Returns empty dict on failure."""
    if not _CAREER_JSON_PATH.exists():
        return {}
    try:
        with open(_CAREER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_json(data: dict) -> None:
    """Atomically write the dict back to careerData.json."""
    os.makedirs(_CAREER_JSON_PATH.parent, exist_ok=True)
    tmp = _CAREER_JSON_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, _CAREER_JSON_PATH)


def career_exists(career_name: str) -> bool:
    """Check whether a career with this name already exists in the JSON."""
    data = _read_json()
    bank = data.get("careerBank", [])
    norm = career_name.strip().lower()
    return any(c.get("careerName", "").strip().lower() == norm for c in bank)


def append_to_json(career_entry: dict) -> bool:
    """
    Append a new career entry to careerData.json if it doesn't already exist.

    Returns True if the entry was added, False if it was a duplicate.
    Thread-safe via file lock.
    """
    with _lock:
        if career_exists(career_entry.get("careerName", "")):
            return False

        data = _read_json()
        if "careerBank" not in data:
            data["careerBank"] = []

        # Assign a new sequential id
        existing_ids = [c.get("id", 0) for c in data["careerBank"]]
        next_id = max(existing_ids, default=0) + 1
        career_entry["id"] = next_id

        data["careerBank"].append(career_entry)
        _write_json(data)
        return True


def get_career_json_path() -> str:
    """Return the absolute path to careerData.json (for external use)."""
    return str(_CAREER_JSON_PATH)