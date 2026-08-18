"""
Mini search engine with fuzzy matching for typo-tolerant career lookups.

Uses a hybrid similarity approach: token-based (word-level) Jaccard similarity
is the primary score, which prevents false matches when careers share common
words like "Scientist" or "Engineer".  Character-level sequence similarity
is used as a fallback so single-word queries and typo corrections still work.
"""

import difflib
import json
import re
from pathlib import Path
from typing import Optional


def _normalize(text: str) -> str:
    """Lowercase, strip, and collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenize(text: str) -> set[str]:
    """Split normalised text into a set of word tokens."""
    return set(text.split())


def _word_sim(word_a: str, word_b: str) -> float:
    """Character-level similarity between two individual words."""
    return difflib.SequenceMatcher(None, word_a, word_b).ratio()


def _similarity(a: str, b: str) -> float:
    """
    Hybrid similarity score that combines word-level fuzzy matching with
    token-based (Jaccard) overlap.

    Algorithm:
    1. Tokenise both strings into words.
    2. For each query word, find the best-matching word in the target.
       If the match is ≥ 0.8 it counts as a "hit" (exact or near-typo).
    3. Final score = matched_words / max(query_words, target_words).

    This prevents "data scientist" from matching "biomedical scientist"
    (only 1 of 2 words match → score 0.5) while still catching typos
    like "data scintist" → "data scientist" (both words match → 1.0).

    For single-word comparisons, falls back to character-level similarity
    so short queries with typos are still tolerated.
    """
    a_tokens = _tokenize(a)
    b_tokens = _tokenize(b)

    if not a_tokens or not b_tokens:
        return 0.0

    # Single-word: use character-level similarity directly
    if len(a_tokens) == 1 and len(b_tokens) == 1:
        return _word_sim(a, b)

    # Multi-word: pair query words with best target word match
    NEAR_MATCH_THRESHOLD = 0.8
    matched = 0
    used: set[str] = set()
    for qw in a_tokens:
        best_score = 0.0
        best_tw = ""
        for tw in b_tokens:
            if tw in used:
                continue
            score = 1.0 if qw == tw else _word_sim(qw, tw)
            if score > best_score:
                best_score = score
                best_tw = tw
        if best_score >= NEAR_MATCH_THRESHOLD and best_tw:
            matched += 1
            used.add(best_tw)

    return matched / max(len(a_tokens), len(b_tokens))


def fuzzy_search_careers(
    query: str,
    careers: list[dict],
    *,
    cutoff: float = 0.6,
    max_results: int = 5,
) -> list[dict]:
    """
    Search a list of career dicts using fuzzy matching on careerName.

    Returns careers sorted by similarity (best match first).  Only
    results with a similarity score >= *cutoff* are included.
    """
    if not query or not careers:
        return []

    norm_query = _normalize(query)

    scored: list[tuple[float, dict]] = []
    seen: set[str] = set()
    for career in careers:
        name = _normalize(career.get("careerName", ""))
        if not name:
            continue
        score = _similarity(norm_query, name)
        if score >= cutoff:
            key = career.get("careerName", "")
            if key not in seen:
                seen.add(key)
                scored.append((score, career))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [career for _, career in scored[:max_results]]


def find_best_match(
    query: str,
    sources: list[list[dict]],
    *,
    cutoff: float = 0.7,
) -> Optional[dict]:
    """
    Try multiple sources (static JSON, DB cache, etc.) and return the best
    match above the cutoff, or None.
    """
    norm_query = _normalize(query)

    # First try exact match across all sources
    for source in sources:
        for career in source:
            if _normalize(career.get("careerName", "")) == norm_query:
                return career

    # Then fuzzy match using hybrid similarity
    best: Optional[dict] = None
    best_score = 0.0
    for source in sources:
        for career in source:
            name = _normalize(career.get("careerName", ""))
            if not name:
                continue
            score = _similarity(norm_query, name)
            if score >= cutoff and score > best_score:
                best_score = score
                best = career

    return best


def load_static_careers(json_path: str) -> list[dict]:
    """Load career entries from a JSON file (careerData.json format)."""
    path = Path(json_path)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(data, dict):
        return data.get("careerBank", [])
    if isinstance(data, list):
        return data
    return []