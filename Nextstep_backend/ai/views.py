import hashlib
import json

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from .gemini import (
    get_gemini_recommendations,
    get_career_recommendation,
    search_career_info,
    generate_resource_library,
    search_resource_info,
)
from .models import AIRecommendation
from .search import (
    find_best_match,
    load_static_careers,
    find_best_resource_matches,
    load_static_resources,
)
from .json_cache import (
    append_to_json,
    get_career_json_path,
    append_resources_to_json,
)

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_input_hash(*parts: str) -> str:
    """Produce a deterministic MD5 hash from one or more input strings."""
    canonical = "|".join(p.strip().lower() for p in parts if p)
    return hashlib.md5(canonical.encode("utf-8")).hexdigest()


def _cache_key(prefix: str, input_hash: str) -> str:
    return f"ai:{prefix}:{input_hash}"


def _resolve_ai_output(
    prefix: str,
    input_hash: str,
    input_data: dict,
    generate_fn,
    user=None,
    recommendation_type: str = "search",
    ttl: int = None,
):
    """
    Three-tier resolution for AI responses:

    1. Django cache (fastest — in-memory or Redis).
    2. AIRecommendation DB table (durable fallback).
    3. Call *generate_fn* (Gemini) — then persist to all three layers.

    Returns (output_data, from_cache: bool).
    """
    if ttl is None:
        ttl = settings.AI_CACHE_TTL.get(recommendation_type, 3600)

    key = _cache_key(prefix, input_hash)

    # 1. Cache
    cached = cache.get(key)
    if cached is not None:
        logger.debug("AI cache HIT: %s", key)
        return cached, True

    # 2. Database
    try:
        db_entry = AIRecommendation.objects.get(
            recommendation_type=recommendation_type,
            input_hash=input_hash,
        )
        output = db_entry.output_data
        cache.set(key, output, timeout=ttl)
        logger.debug("AI DB HIT: %s", key)
        return output, True
    except AIRecommendation.DoesNotExist:
        pass

    # 3. Generate
    logger.info("AI cache MISS — calling Gemini: %s", key)
    try:
        output = generate_fn()
    except Exception as exc:
        logger.exception("Gemini generation failed")
        return {"error": str(exc)}, False

    # Persist
    cache.set(key, output, timeout=ttl)
    AIRecommendation.objects.create(
        user=user,
        input_hash=input_hash,
        input_data=input_data,
        output_data=output,
        recommendation_type=recommendation_type,
    )
    return output, False


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class CareerRecommendationView(APIView):
    """
    Quiz-based career recommendations (3 careers).
    Cached by hash of quiz responses.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        user_responses = request.data

        if not user_responses or 'responses' not in user_responses:
            logger.warning("Career recommendation request with invalid input.")
            return Response(
                {"error": "Invalid input. 'responses' key is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        input_hash = _make_input_hash(json.dumps(user_responses, sort_keys=True))

        def _generate():
            recommendations = get_gemini_recommendations(user_responses)
            if not recommendations:
                raise Exception("Gemini returned no recommendations.")
            return recommendations

        output, from_cache = _resolve_ai_output(
            prefix="quiz",
            input_hash=input_hash,
            input_data=user_responses,
            generate_fn=_generate,
            user=request.user,
            recommendation_type="quiz",
        )

        if "error" in output:
            return Response(
                {"error": "Could not generate recommendations at this time. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(output, status=status.HTTP_200_OK)


class CareerDetailRecommendationView(APIView):
    """
    Per-career detail recommendation (insight + related career + video).
    Cached by hash of career data + user type.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        career_data = request.data.get('career')
        user_type = request.data.get('userType')

        if not career_data or 'careerName' not in career_data:
            logger.warning("Career detail recommendation request with invalid career data.")
            return Response(
                {"error": "Invalid input. 'career' object with 'careerName' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        input_hash = _make_input_hash(
            json.dumps(career_data, sort_keys=True),
            user_type or "",
        )

        def _generate():
            recommendation = get_career_recommendation(career_data, user_type)
            if not recommendation:
                raise Exception("Gemini returned no recommendation.")
            return recommendation

        output, from_cache = _resolve_ai_output(
            prefix="detail",
            input_hash=input_hash,
            input_data={"career": career_data, "userType": user_type},
            generate_fn=_generate,
            user=request.user,
            recommendation_type="career_detail",
        )

        if "error" in output:
            return Response(
                {"error": "Could not generate recommendation at this time. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(output, status=status.HTTP_200_OK)


class CareerSearchView(APIView):
    """
    Free-text career search with AI fallback.

    Flow:
    1. Check static JSON (careerData.json) — exact + fuzzy match.
    2. Check DB cache (AIRecommendation) — fuzzy match.
    3. Call Gemini via search_career_info().
    4. Persist result to cache, DB, and append to careerData.json.

    Request:  { "query": "data scientist", "userType": "student" }
    Response: { "career": {...}, "fromCache": true|false }
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        query = (request.data.get("query") or "").strip()
        user_type = request.data.get("userType")

        if not query:
            return Response(
                {"error": "Query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Check static JSON (exact + fuzzy)
        json_path = get_career_json_path()
        static_careers = load_static_careers(json_path)

        match = find_best_match(query, [static_careers], cutoff=0.7)
        if match:
            logger.info("Career search: static JSON match for '%s' → '%s'", query, match.get("careerName"))
            return Response({"career": match, "fromCache": True}, status=status.HTTP_200_OK)

        # 2. Check DB cache (fuzzy)
        db_entries = AIRecommendation.objects.filter(
            recommendation_type="search",
        ).values_list("output_data", flat=True)

        db_careers = []
        for entry in db_entries:
            if isinstance(entry, dict) and "careerName" in entry:
                db_careers.append(entry)
            elif isinstance(entry, dict) and "career" in entry:
                db_careers.append(entry["career"])

        match = find_best_match(query, [db_careers], cutoff=0.7)
        if match:
            logger.info("Career search: DB match for '%s' → '%s'", query, match.get("careerName"))
            return Response({"career": match, "fromCache": True}, status=status.HTTP_200_OK)

        # 3. Call Gemini
        input_hash = _make_input_hash(query, user_type or "")

        def _generate():
            result = search_career_info(query, user_type)
            if "error" in result:
                raise Exception(result["error"])
            return result

        output, from_cache = _resolve_ai_output(
            prefix="search",
            input_hash=input_hash,
            input_data={"query": query, "userType": user_type},
            generate_fn=_generate,
            user=request.user,
            recommendation_type="search",
            ttl=settings.AI_CACHE_TTL.get("career_search", 3600),
        )

        if "error" in output:
            return Response(
                {"error": "Could not generate career data for this search. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 4. Append to static JSON for future instant matches
        appended = append_to_json(output)
        logger.info(
            "Career search: AI generated '%s' — appended to JSON: %s",
            output.get("careerName"),
            appended,
        )

        return Response({"career": output, "fromCache": False}, status=status.HTTP_200_OK)


class ResourceLibraryGenerateView(APIView):
    """
    Generate a realistic AI-powered resource library set.

    Request:  { "topic": "data analytics", "userType": "student", "limit": 12 }
    Response: { "resources": [...], "fromCache": true|false, "appended": 10 }
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        topic = (request.data.get("topic") or "career development").strip()
        user_type = request.data.get("userType")
        limit = request.data.get("limit", 12)

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 12
        limit = max(4, min(limit, 24))

        input_hash = _make_input_hash(topic, user_type or "", str(limit))

        def _generate():
            return generate_resource_library(topic=topic, user_type=user_type or 'student', limit=limit)

        output, from_cache = _resolve_ai_output(
            prefix="resource-library",
            input_hash=input_hash,
            input_data={"topic": topic, "userType": user_type, "limit": limit},
            generate_fn=_generate,
            user=request.user,
            recommendation_type="resource_library",
            ttl=settings.AI_CACHE_TTL.get("resource_library", 21600),
        )

        if isinstance(output, dict) and "error" in output:
            return Response(
                {"error": "Could not generate resource library right now. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        resources = output if isinstance(output, list) else []
        appended = append_resources_to_json(resources)
        return Response(
            {
                "resources": resources,
                "fromCache": from_cache,
                "appended": appended,
            },
            status=status.HTTP_200_OK,
        )


class ResourceSearchView(APIView):
    """
    Resource search with static + DB cache + AI fallback.

    Request:  { "query": "resume template", "userType": "student", "limit": 8 }
    Response: { "resources": [...], "fromCache": true|false, "source": "static|db|ai" }
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai'

    def post(self, request, *args, **kwargs):
        query = (request.data.get("query") or "").strip()
        user_type = request.data.get("userType")
        limit = request.data.get("limit", 8)

        if not query:
            return Response(
                {"error": "Query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 8
        limit = max(1, min(limit, 12))

        json_path = get_career_json_path()

        static_resources = load_static_resources(json_path)
        static_matches = find_best_resource_matches(
            query,
            [static_resources],
            cutoff=0.55,
            max_results=limit,
        )
        if static_matches:
            return Response(
                {"resources": static_matches, "fromCache": True, "source": "static"},
                status=status.HTTP_200_OK,
            )

        db_entries = AIRecommendation.objects.filter(
            recommendation_type__in=["resource_search", "resource_library"],
        ).values_list("output_data", flat=True)

        db_resources: list[dict] = []
        for entry in db_entries:
            if isinstance(entry, list):
                db_resources.extend([item for item in entry if isinstance(item, dict)])
            elif isinstance(entry, dict) and isinstance(entry.get("resources"), list):
                db_resources.extend([item for item in entry["resources"] if isinstance(item, dict)])

        db_matches = find_best_resource_matches(
            query,
            [db_resources],
            cutoff=0.55,
            max_results=limit,
        )
        if db_matches:
            return Response(
                {"resources": db_matches, "fromCache": True, "source": "db"},
                status=status.HTTP_200_OK,
            )

        input_hash = _make_input_hash(query, user_type or "", str(limit))

        def _generate():
            return search_resource_info(query=query, user_type=user_type or 'student', limit=limit)

        output, from_cache = _resolve_ai_output(
            prefix="resource-search",
            input_hash=input_hash,
            input_data={"query": query, "userType": user_type, "limit": limit},
            generate_fn=_generate,
            user=request.user,
            recommendation_type="resource_search",
            ttl=settings.AI_CACHE_TTL.get("resource_search", 3600),
        )

        if isinstance(output, dict) and "error" in output:
            return Response(
                {"error": "Could not search resources at this time. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        resources = output if isinstance(output, list) else []
        append_resources_to_json(resources)

        return Response(
            {"resources": resources, "fromCache": from_cache, "source": "ai"},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# AI API flow (ai.views)
# ---------------------------------------------------------------------------
# - `CareerRecommendationView`: Quiz-based → 3 career recommendations.
#   Cached by hash of the quiz responses payload.
# - `CareerDetailRecommendationView`: Per-career insight + video.
#   Cached by hash of career data + user type.
# - `CareerSearchView`: Free-text search with three-tier resolution:
#   static JSON → DB cache → Gemini.  New results are persisted to all
#   three layers and appended to careerData.json.
#
# Cache architecture:
#   Layer 1 — Django cache (locmem in dev, Redis in prod) — fastest.
#   Layer 2 — AIRecommendation DB table — durable, survives restarts.
#   Layer 3 — Gemini API — expensive, called only on cache miss.
#
# All views use scoped throttling ('ai') to protect the Gemini quota.
# ---------------------------------------------------------------------------