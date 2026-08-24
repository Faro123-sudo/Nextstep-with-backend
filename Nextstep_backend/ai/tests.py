"""
Tests for the AI app: model, cache resolution, search utilities, and JSON cache.

These tests use Django's TestCase and mock the Gemini client so no real API
calls are made during test runs.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from .models import AIRecommendation
from .search import (
    fuzzy_search_careers,
    find_best_match,
    load_static_careers,
    fuzzy_search_resources,
    find_best_resource_matches,
    load_static_resources,
)
from .json_cache import (
    append_to_json,
    career_exists,
    get_career_json_path,
    append_resources_to_json,
    resource_exists,
)


User = get_user_model()


# ---------------------------------------------------------------------------
# AIRecommendation model tests
# ---------------------------------------------------------------------------

class AIRecommendationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.input_hash = hashlib.md5(b"test query").hexdigest()

    def test_create_recommendation(self):
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type="search",
            input_hash=self.input_hash,
            input_data={"query": "data scientist"},
            output_data={"careerName": "Data Scientist", "description": "Test"},
        )
        self.assertEqual(rec.recommendation_type, "search")
        self.assertEqual(rec.input_hash, self.input_hash)
        self.assertEqual(rec.output_data["careerName"], "Data Scientist")
        self.assertIsNotNone(rec.created_at)
        self.assertIsNotNone(rec.accessed_at)

    def test_unique_input_hash(self):
        AIRecommendation.objects.create(
            input_hash=self.input_hash,
            recommendation_type="search",
            input_data={},
            output_data={},
        )
        with self.assertRaises(Exception):
            AIRecommendation.objects.create(
                input_hash=self.input_hash,
                recommendation_type="search",
                input_data={},
                output_data={},
            )

    def test_nullable_user_and_career(self):
        rec = AIRecommendation.objects.create(
            recommendation_type="quiz",
            input_hash=hashlib.md5(b"no user").hexdigest(),
            input_data={},
            output_data={},
        )
        self.assertIsNone(rec.user)
        self.assertIsNone(rec.career)

    def test_str_representation(self):
        h = hashlib.md5(b"str test").hexdigest()
        rec = AIRecommendation.objects.create(
            recommendation_type="search",
            input_hash=h,
            input_data={},
            output_data={},
        )
        expected = f"AIRecommendation(search) — {h[:12]}"
        self.assertEqual(str(rec), expected)

    def test_default_input_data(self):
        rec = AIRecommendation.objects.create(
            recommendation_type="career_detail",
            input_hash=hashlib.md5(b"defaults").hexdigest(),
            output_data={},
        )
        self.assertEqual(rec.input_data, {})

    def test_ordering(self):
        h1 = hashlib.md5(b"first").hexdigest()
        h2 = hashlib.md5(b"second").hexdigest()
        r1 = AIRecommendation.objects.create(
            recommendation_type="search", input_hash=h1, input_data={}, output_data={}
        )
        r2 = AIRecommendation.objects.create(
            recommendation_type="search", input_hash=h2, input_data={}, output_data={}
        )
        qs = AIRecommendation.objects.all()
        self.assertEqual(qs[0], r2)  # newest first
        self.assertEqual(qs[1], r1)


# ---------------------------------------------------------------------------
# Fuzzy search utility tests
# ---------------------------------------------------------------------------

class SearchUtilityTests(TestCase):
    def setUp(self):
        self.careers = [
            {"careerName": "Data Scientist", "industry": "Technology"},
            {"careerName": "UX Designer", "industry": "Technology"},
            {"careerName": "Software Engineer", "industry": "Technology"},
            {"careerName": "Biomedical Scientist", "industry": "Healthcare"},
            {"careerName": "Graphic Designer", "industry": "Creative"},
        ]
        self.resources = [
            {
                "type": "Article",
                "title": "Data Analyst Interview Guide",
                "description": "Prepare for analytics interviews with sample questions.",
                "url": "https://example.com/data-analyst-guide",
                "tags": ["analytics", "interview"],
            },
            {
                "type": "Template",
                "title": "ATS Resume Template",
                "description": "Resume format optimized for applicant tracking systems.",
                "url": "https://example.com/ats-template",
                "tags": ["resume", "job-search"],
            },
            {
                "type": "Webinar",
                "title": "Breaking into Cybersecurity",
                "description": "Live Q&A with security engineers.",
                "url": "https://example.com/cyber-webinar",
                "tags": ["security", "career"],
            },
        ]

    def test_fuzzy_search_exact_match(self):
        results = fuzzy_search_careers("Data Scientist", self.careers)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["careerName"], "Data Scientist")

    def test_fuzzy_search_typo(self):
        results = fuzzy_search_careers("data scintist", self.careers, cutoff=0.6)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["careerName"], "Data Scientist")

    def test_fuzzy_search_no_match(self):
        results = fuzzy_search_careers("quantum physicist", self.careers, cutoff=0.8)
        self.assertEqual(len(results), 0)

    def test_fuzzy_search_empty_query(self):
        results = fuzzy_search_careers("", self.careers)
        self.assertEqual(len(results), 0)

    def test_fuzzy_search_empty_careers(self):
        results = fuzzy_search_careers("engineer", [])
        self.assertEqual(len(results), 0)

    def test_fuzzy_search_max_results(self):
        results = fuzzy_search_careers("designer", self.careers, cutoff=0.3, max_results=2)
        self.assertLessEqual(len(results), 2)

    def test_find_best_match_exact(self):
        match = find_best_match("UX Designer", [self.careers])
        self.assertIsNotNone(match)
        self.assertEqual(match["careerName"], "UX Designer")

    def test_find_best_match_fuzzy(self):
        match = find_best_match("ux desiner", [self.careers], cutoff=0.6)
        self.assertIsNotNone(match)
        self.assertEqual(match["careerName"], "UX Designer")

    def test_find_best_match_no_match(self):
        match = find_best_match("zookeeper", [self.careers], cutoff=0.9)
        self.assertIsNone(match)

    def test_find_best_match_multiple_sources(self):
        source_a = [{"careerName": "Data Scientist"}]
        source_b = [{"careerName": "UX Designer"}]
        match = find_best_match("UX Designer", [source_a, source_b])
        self.assertIsNotNone(match)
        self.assertEqual(match["careerName"], "UX Designer")

    def test_find_best_match_with_audience(self):
        careers_with_audience = [
            {"careerName": "Data Scientist", "audiences": ["student", "graduate"]},
            {"careerName": "UX Designer", "audiences": ["professional"]},
        ]
        match = find_best_match("Data Scientist", [careers_with_audience])
        self.assertIsNotNone(match)
        self.assertEqual(match["careerName"], "Data Scientist")

    def test_load_static_careers_valid_json(self):
        data = {"careerBank": [{"careerName": "Test Career"}]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            tmp_path = f.name
        try:
            careers = load_static_careers(tmp_path)
            self.assertEqual(len(careers), 1)
            self.assertEqual(careers[0]["careerName"], "Test Career")
        finally:
            os.unlink(tmp_path)

    def test_load_static_careers_list_format(self):
        data = [{"careerName": "Career A"}, {"careerName": "Career B"}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            tmp_path = f.name
        try:
            careers = load_static_careers(tmp_path)
            self.assertEqual(len(careers), 2)
        finally:
            os.unlink(tmp_path)

    def test_load_static_careers_file_not_found(self):
        careers = load_static_careers("/nonexistent/path.json")
        self.assertEqual(careers, [])

    def test_load_static_careers_invalid_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("not json")
            tmp_path = f.name
        try:
            careers = load_static_careers(tmp_path)
            self.assertEqual(careers, [])
        finally:
            os.unlink(tmp_path)

    def test_fuzzy_search_resources_exact_title(self):
        results = fuzzy_search_resources("ATS Resume Template", self.resources)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["title"], "ATS Resume Template")

    def test_fuzzy_search_resources_description_match(self):
        results = fuzzy_search_resources("applicant tracking", self.resources)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["title"], "ATS Resume Template")

    def test_find_best_resource_matches_multiple_sources(self):
        source_a = [self.resources[0]]
        source_b = [self.resources[1]]
        matches = find_best_resource_matches("resume", [source_a, source_b], max_results=3)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]["title"], "ATS Resume Template")

    def test_load_static_resources_valid_json(self):
        payload = {
            "resourceLibrary": {
                "articles": [{"title": "Article A", "type": "Article", "description": "d", "url": "#"}],
                "ebooks": [{"title": "E-book B", "type": "E-book", "description": "d", "url": "#"}],
                "webinars": [],
                "templates": [],
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(payload, f)
            tmp_path = f.name

        try:
            resources = load_static_resources(tmp_path)
            self.assertEqual(len(resources), 2)
            titles = [r["title"] for r in resources]
            self.assertIn("Article A", titles)
            self.assertIn("E-book B", titles)
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# JSON cache utility tests
# ---------------------------------------------------------------------------

class JsonCacheTests(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.json_path = Path(self.tmp_dir) / "careerData.json"
        # Seed with initial data
        initial = {
            "careerBank": [
                {"id": 1, "careerName": "Data Scientist", "industry": "Technology"},
                {"id": 2, "careerName": "UX Designer", "industry": "Technology"},
            ],
            "resourceLibrary": {
                "articles": [
                    {
                        "id": "art1",
                        "type": "Article",
                        "title": "Interview Preparation Checklist",
                        "description": "Checklist for interviews.",
                        "url": "#",
                    }
                ],
                "ebooks": [],
                "webinars": [],
                "templates": [],
            },
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(initial, f)

    def tearDown(self):
        if self.json_path.exists():
            os.unlink(self.json_path)
        os.rmdir(self.tmp_dir)

    def test_career_exists_found(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            self.assertTrue(career_exists("Data Scientist"))
            self.assertTrue(career_exists("ux designer"))
            self.assertFalse(career_exists("Biomedical Scientist"))

    def test_append_to_json_new_career(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            new_entry = {"careerName": "Biomedical Scientist", "industry": "Healthcare"}
            result = append_to_json(new_entry)
            self.assertTrue(result)

            # Verify it was written
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            names = [c["careerName"] for c in data["careerBank"]]
            self.assertIn("Biomedical Scientist", names)
            # Should have an auto-assigned id
            self.assertIn("id", data["careerBank"][-1])

    def test_append_to_json_duplicate(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            new_entry = {"careerName": "Data Scientist", "industry": "Technology"}
            result = append_to_json(new_entry)
            self.assertFalse(result)

    def test_append_to_json_empty_bank(self):
        # Overwrite with empty bank
        initial = {}
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(initial, f)

        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            new_entry = {"careerName": "New Career", "industry": "Tech"}
            result = append_to_json(new_entry)
            self.assertTrue(result)

            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("careerBank", data)
            self.assertEqual(len(data["careerBank"]), 1)
            self.assertEqual(data["careerBank"][0]["id"], 1)

    def test_get_career_json_path(self):
        path = get_career_json_path()
        self.assertIsInstance(path, str)
        self.assertTrue(path.endswith("careerData.json"))

    def test_resource_exists_found(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            self.assertTrue(resource_exists("Interview Preparation Checklist"))
            self.assertTrue(resource_exists("interview preparation checklist"))
            self.assertFalse(resource_exists("Cloud Portfolio Template"))

    def test_append_resources_to_json(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            added = append_resources_to_json([
                {
                    "type": "Template",
                    "title": "Cloud Portfolio Template",
                    "description": "A one-page cloud engineer portfolio layout.",
                    "url": "#",
                    "tags": ["cloud", "portfolio"],
                }
            ])
            self.assertEqual(added, 1)

            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(len(data["resourceLibrary"]["templates"]), 1)
            self.assertEqual(
                data["resourceLibrary"]["templates"][0]["title"],
                "Cloud Portfolio Template",
            )

    def test_append_resources_to_json_duplicate(self):
        with patch("ai.json_cache._CAREER_JSON_PATH", self.json_path):
            added = append_resources_to_json([
                {
                    "type": "Article",
                    "title": "Interview Preparation Checklist",
                    "description": "Duplicate",
                    "url": "#",
                }
            ])
            self.assertEqual(added, 0)


# ---------------------------------------------------------------------------
# Cache resolution helper tests
# ---------------------------------------------------------------------------

class CacheResolutionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cacheuser", password="testpass123"
        )
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_cache_hit(self):
        """Test that cache returns the value on second call."""
        from .views import _make_input_hash, _cache_key, _resolve_ai_output

        input_hash = _make_input_hash("test query")
        key = _cache_key("search", input_hash)

        # Seed the cache
        expected = {"careerName": "Test Career"}
        cache.set(key, expected, timeout=300)

        def _generate():
            raise AssertionError("Should not be called on cache hit")

        output, from_cache = _resolve_ai_output(
            prefix="search",
            input_hash=input_hash,
            input_data={"query": "test query"},
            generate_fn=_generate,
            recommendation_type="search",
            ttl=300,
        )
        self.assertEqual(output, expected)
        self.assertTrue(from_cache)

    def test_db_hit(self):
        """Test that DB value is returned when cache is empty."""
        from .views import _make_input_hash, _resolve_ai_output

        input_hash = _make_input_hash("db test")
        expected = {"careerName": "DB Career"}
        AIRecommendation.objects.create(
            recommendation_type="search",
            input_hash=input_hash,
            input_data={},
            output_data=expected,
        )

        def _generate():
            raise AssertionError("Should not be called on DB hit")

        output, from_cache = _resolve_ai_output(
            prefix="search",
            input_hash=input_hash,
            input_data={"query": "db test"},
            generate_fn=_generate,
            recommendation_type="search",
            ttl=300,
        )
        self.assertEqual(output, expected)
        self.assertTrue(from_cache)

    def test_generate_on_miss(self):
        """Test that generate_fn is called when both cache and DB are empty."""
        from .views import _make_input_hash, _resolve_ai_output

        input_hash = _make_input_hash("miss test")
        expected = {"careerName": "Generated Career"}

        def _generate():
            return expected

        output, from_cache = _resolve_ai_output(
            prefix="search",
            input_hash=input_hash,
            input_data={"query": "miss test"},
            generate_fn=_generate,
            recommendation_type="search",
            ttl=300,
        )
        self.assertEqual(output, expected)
        self.assertFalse(from_cache)

        # Verify it was persisted to DB
        self.assertTrue(
            AIRecommendation.objects.filter(input_hash=input_hash).exists()
        )

    def test_generate_error_returns_error_dict(self):
        """Test that exceptions from generate_fn are caught and returned."""
        from .views import _make_input_hash, _resolve_ai_output

        input_hash = _make_input_hash("error test")

        def _generate():
            raise ValueError("Gemini API error")

        output, from_cache = _resolve_ai_output(
            prefix="search",
            input_hash=input_hash,
            input_data={"query": "error test"},
            generate_fn=_generate,
            recommendation_type="search",
            ttl=300,
        )
        self.assertIn("error", output)
        self.assertFalse(from_cache)

    def test_input_hash_consistency(self):
        """Test that same inputs produce the same hash."""
        from .views import _make_input_hash

        h1 = _make_input_hash("hello world")
        h2 = _make_input_hash("hello world")
        self.assertEqual(h1, h2)

    def test_input_hash_case_insensitive(self):
        """Test that input hash is case-insensitive."""
        from .views import _make_input_hash

        h1 = _make_input_hash("Data Scientist")
        h2 = _make_input_hash("data scientist")
        self.assertEqual(h1, h2)


# ---------------------------------------------------------------------------
# API endpoint tests (with mocked Gemini)
# ---------------------------------------------------------------------------

class CareerSearchViewTests(TestCase):
    """Test the CareerSearchView endpoint with a mocked Gemini client."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="searchuser", password="testpass123"
        )
        # Obtain JWT token
        response = self.client.post("/api/accounts/login/", {
            "username": "searchuser",
            "password": "testpass123",
        }, format="json")
        # If login endpoint doesn't exist or fails, fall back to force_authenticate
        if response.status_code == 200:
            self.token = response.data.get("access")
        else:
            self.token = None
            self.client.force_authenticate(user=self.user)
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _auth_header(self):
        if self.token:
            return {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}
        return {}

    @patch("ai.views.search_career_info")
    def test_search_missing_query(self, mock_search):
        """Test that missing query returns 400."""
        response = self.client.post(
            "/api/ai/search/",
            {},
            format="json",
            **self._auth_header(),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        mock_search.assert_not_called()

    @patch("ai.views.search_career_info")
    def test_search_empty_query(self, mock_search):
        """Test that empty query returns 400."""
        response = self.client.post(
            "/api/ai/search/",
            {"query": ""},
            format="json",
            **self._auth_header(),
        )
        self.assertEqual(response.status_code, 400)
        mock_search.assert_not_called()

    @patch("ai.views.find_best_match")
    def test_search_static_json_hit(self, mock_find_best_match):
        """Test that a static JSON match returns immediately."""
        mock_find_best_match.return_value = {
            "careerName": "Data Scientist",
            "industry": "Technology",
        }
        response = self.client.post(
            "/api/ai/search/",
            {"query": "Data Scientist"},
            format="json",
            **self._auth_header(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["fromCache"])
        self.assertEqual(response.data["career"]["careerName"], "Data Scientist")

    @patch("ai.views.search_career_info")
    @patch("ai.views.find_best_match")
    def test_search_ai_fallback(self, mock_find_best_match, mock_search_info):
        """Test AI fallback when no static match is found."""
        mock_find_best_match.return_value = None  # No static match
        mock_search_info.return_value = {
            "careerName": "Quantum Physicist",
            "industry": "Science",
            "description": "Studies quantum mechanics",
            "averageSalary": "$120,000",
            "educationPath": "PhD in Physics",
            "jobOutlook": "Growing",
            "dayInTheLife": "Research and experiments",
            "skillsRequired": ["Quantum Mechanics", "Math"],
            "relatedRoles": ["Theoretical Physicist"],
            "audiences": ["student", "graduate"],
            "careerInsight": "A challenging but rewarding field.",
        }

        response = self.client.post(
            "/api/ai/search/",
            {"query": "Quantum Physicist", "userType": "student"},
            format="json",
            **self._auth_header(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["fromCache"])
        self.assertEqual(
            response.data["career"]["careerName"], "Quantum Physicist"
        )

    @patch("ai.views.search_career_info")
    @patch("ai.views.find_best_match")
    def test_search_ai_error(self, mock_find_best_match, mock_search_info):
        """Test that AI errors return a 500."""
        mock_find_best_match.return_value = None
        mock_search_info.return_value = {"error": "Gemini failed"}

        response = self.client.post(
            "/api/ai/search/",
            {"query": "Unknown Career"},
            format="json",
            **self._auth_header(),
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)


class CareerRecommendationViewTests(TestCase):
    """Test the quiz-based recommendation endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="quizuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("ai.views.get_gemini_recommendations")
    def test_missing_responses(self, mock_rec):
        response = self.client.post(
            "/api/ai/recommend/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        mock_rec.assert_not_called()

    @patch("ai.views.get_gemini_recommendations")
    def test_successful_recommendation(self, mock_rec):
        mock_rec.return_value = [
            {"career": "Data Scientist", "reason": "Good fit"},
            {"career": "UX Designer", "reason": "Creative role"},
            {"career": "Software Engineer", "reason": "Tech skills"},
        ]
        response = self.client.post(
            "/api/ai/recommend/",
            {"responses": [{"question": "Interest", "answer": "Technology"}]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    @patch("ai.views.get_gemini_recommendations")
    def test_cached_recommendation(self, mock_rec):
        mock_rec.return_value = [
            {"career": "Data Scientist", "reason": "Good fit"},
        ]
        # First call — should hit Gemini
        response1 = self.client.post(
            "/api/ai/recommend/",
            {"responses": [{"question": "Q", "answer": "A"}]},
            format="json",
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(mock_rec.call_count, 1)

        # Second call with same data — should get from cache, Gemini not called again
        response2 = self.client.post(
            "/api/ai/recommend/",
            {"responses": [{"question": "Q", "answer": "A"}]},
            format="json",
        )
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(mock_rec.call_count, 1)  # Still 1 — no new call


class CareerDetailRecommendationViewTests(TestCase):
    """Test the per-career detail recommendation endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="detailuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("ai.views.get_career_recommendation")
    def test_missing_career_data(self, mock_rec):
        response = self.client.post(
            "/api/ai/recommend-detail/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        mock_rec.assert_not_called()

    @patch("ai.views.get_career_recommendation")
    def test_missing_career_name(self, mock_rec):
        response = self.client.post(
            "/api/ai/recommend-detail/",
            {"career": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        mock_rec.assert_not_called()

    @patch("ai.views.get_career_recommendation")
    def test_successful_detail(self, mock_rec):
        mock_rec.return_value = {
            "recommendation": "Great career choice",
            "relatedCareer": "ML Engineer",
            "resourceUrl": "https://youtube.com/embed/test123",
        }
        response = self.client.post(
            "/api/ai/recommend-detail/",
            {
                "career": {"careerName": "Data Scientist", "industry": "Tech"},
                "userType": "student",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["recommendation"], "Great career choice")
        self.assertEqual(response.data["relatedCareer"], "ML Engineer")


class ResourceLibraryViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="resourceuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("ai.views.generate_resource_library")
    def test_generate_resource_library_success(self, mock_generate):
        mock_generate.return_value = [
            {
                "type": "Article",
                "title": "How to Build a Strong Resume",
                "description": "Practical guide for entry-level candidates.",
                "url": "#",
            }
        ]

        response = self.client.post(
            "/api/ai/resources/generate/",
            {"topic": "resume", "limit": 6},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("resources", response.data)
        self.assertEqual(len(response.data["resources"]), 1)

    def test_resource_search_missing_query(self):
        response = self.client.post(
            "/api/ai/resources/search/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    @patch("ai.views.search_resource_info")
    @patch("ai.views.find_best_resource_matches")
    def test_resource_search_ai_fallback(self, mock_matches, mock_search):
        # No static or DB matches, then AI fallback
        mock_matches.return_value = []
        mock_search.return_value = [
            {
                "type": "Template",
                "title": "Backend Developer Resume Template",
                "description": "ATS-friendly layout for backend roles.",
                "url": "#",
            }
        ]

        response = self.client.post(
            "/api/ai/resources/search/",
            {"query": "backend resume", "limit": 5},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("resources", response.data)
        self.assertEqual(response.data["source"], "ai")