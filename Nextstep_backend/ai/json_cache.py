"""
Thread-safe read/write helpers for the frontend careerData.json file.

When the AI generates a new career entry that didn't exist in the static
JSON, we append it so future searches hit the file directly without
consuming Gemini tokens.
"""

import json
import os
import re
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


def _normalise_resource_type(resource_type: str) -> str:
    raw = (resource_type or "").strip().lower()
    mapping = {
        "article": "articles",
        "e-book": "ebooks",
        "ebook": "ebooks",
        "webinar": "webinars",
        "template": "templates",
    }
    return mapping.get(raw, "articles")


def _next_resource_id(resources: list[dict]) -> str:
    """Return the next ai-generated resource id as aires<N>."""
    max_num = 0
    for item in resources:
        rid = str(item.get("id", ""))
        match = re.search(r"(\d+)$", rid)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"aires{max_num + 1}"


def load_resource_library() -> list[dict]:
    """Load all resources from resourceLibrary as one flattened list."""
    data = _read_json()
    library = data.get("resourceLibrary", {})
    if not isinstance(library, dict):
        return []

    items: list[dict] = []
    for bucket in ("articles", "ebooks", "webinars", "templates"):
        values = library.get(bucket, [])
        if isinstance(values, list):
            items.extend([v for v in values if isinstance(v, dict)])
    return items


def resource_exists(title: str) -> bool:
    """Check whether a resource title already exists (case-insensitive)."""
    norm = (title or "").strip().lower()
    if not norm:
        return False
    return any((r.get("title", "").strip().lower() == norm) for r in load_resource_library())


def append_resources_to_json(resources: list[dict]) -> int:
    """
    Append new resources to resourceLibrary buckets.

    Returns the number of resources actually added.
    """
    if not resources:
        return 0

    with _lock:
        data = _read_json()
        if "resourceLibrary" not in data or not isinstance(data["resourceLibrary"], dict):
            data["resourceLibrary"] = {}

        library = data["resourceLibrary"]
        for bucket in ("articles", "ebooks", "webinars", "templates"):
            if bucket not in library or not isinstance(library[bucket], list):
                library[bucket] = []

        existing = []
        for bucket in ("articles", "ebooks", "webinars", "templates"):
            existing.extend([item for item in library[bucket] if isinstance(item, dict)])

        existing_titles = {
            item.get("title", "").strip().lower()
            for item in existing
            if item.get("title")
        }

        added = 0
        for item in resources:
            if not isinstance(item, dict):
                continue

            title = (item.get("title") or "").strip()
            if not title:
                continue

            norm_title = title.lower()
            if norm_title in existing_titles:
                continue

            resource_type = item.get("type", "Article")
            bucket = _normalise_resource_type(resource_type)

            new_item = {
                "id": item.get("id") or _next_resource_id(existing),
                "type": resource_type,
                "title": title,
                "description": (item.get("description") or "").strip(),
                "url": (item.get("url") or "#").strip() or "#",
            }
            if isinstance(item.get("tags"), list):
                new_item["tags"] = [str(t).strip() for t in item["tags"] if str(t).strip()]

            library[bucket].append(new_item)
            existing.append(new_item)
            existing_titles.add(norm_title)
            added += 1

        if added:
            _write_json(data)

        return added