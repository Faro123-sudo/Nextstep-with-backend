# Plan: AI Career Data Caching & Search Enhancement

## 1. Backend: Cache Configuration `settings.py`
- Add explicit `CACHES` config using Django’s `locmem` backend. No Docker/Redis needed for dev
- Document Redis option for future production scaling
- Set appropriate TTLs: 
    - `24h` for career data
    - `1h` for search results

## 2. Backend: AI Recommendation Model `ai/models.py`
* Create `AIRecommendation` model:
    - `user` | FK to User | nullable |
    - `career` | FK to `core.Career` | nullable |
    - `input_hash` | CharField, unique | MD5 hash of the query for dedup
    - `input_data` | JSONField | original request payload
    - `output_data` | JSONField | Gemini response
    - `recommendation_type` | CharField with choices | `quiz` / `career_detail` / `search`
    - `created_at` | DateTimeField | auto_now_add
    - `accessed_at` | DateTimeField | auto_now
* Run migration: `python manage.py makemigrations && migrate`

## 3. Backend: Master Search Prompt `ai/gemini.py`
Add `search_career_info(query: str, user_type: str = None) -> dict`

*Function:*
- Takes a free-text search query e.g. `“data scientist”`, `“ux designer”`
- Returns structured career data matching the `careerData.json` schema:
  `careerName, description, skillsRequired, industry, averageSalary, educationPath, jobOutlook, dayInTheLife, relatedRoles, careerInsight, careerVideo`
- Uses schema-backed Gemini prompt for structured JSON output

## 4. Backend: Cache + DB + JSON Persistence Layer `ai/views.py`
Add `CareerSearchView` → `POST /api/ai/search/`

*Cache-first flow for all AI endpoints:*
1. Compute `input_hash` from request payload
2. Check Django cache → if hit, return immediately
3. Check `AIRecommendation` DB → if hit, populate cache, return
4. Check static JSON file → if found, return. No AI call
5. Call Gemini → save to cache, DB, AND append to `careerData.json`

Also add the same caching logic to:
- `CareerRecommendationView`
- `CareerDetailRecommendationView`

## 5. Backend: Mini Search Engine `ai/search.py`
Utility using Python’s `difflib.get_close_matches` for fuzzy matching

- Applied against: static JSON data + cached DB entries
- Tolerates typos/misspellings e.g. `“data scintist”` → `“data scientist”`
- Returns closest matches with similarity scores
- Falls back to Gemini if no good match

## 6. Backend: JSON File Management `ai/json_cache.py`
Utility to read/write `careerData.json` — the frontend’s static file

- `append_to_json(career_entry)` — appends new AI-generated career to the JSON array
- Thread-safe with file locking
- Deduplication by career name

## 7. Backend: Seed Career Data `core/management/commands/seed_careers.py`
Django management command to seed `core.Career` model from `careerData.json`

- Maps JSON fields to `Career` model fields
- Creates `Skill` and `Tag` objects as needed

## 8. Frontend: AI Search Fallback `CareerBank.jsx`
- When user search yields 0 results from static JSON, trigger backend AI search
- Show loading state with Lottie animation
- Display AI-generated results inline
- On success, the career is now in the JSON for future searches

## 9. Frontend: Fuzzy Search Enhancement
- Add client-side fuzzy matching using a simple Levenshtein-based approach on the loaded JSON data
- Improves UX before falling back to backend AI search

---

### Files to Create/Modify
File | Action
`Nextstep_backend/nextstep/settings.py` | Add `CACHES` config
`Nextstep_backend/ai/models.py` | Add `AIRecommendation` model
`Nextstep_backend/ai/gemini.py` | Add `search_career_info()`
`Nextstep_backend/ai/views.py` | Add `CareerSearchView` + cache logic to existing views
`Nextstep_backend/ai/urls.py` | Add search route
`Nextstep_backend/ai/search.py` | New — fuzzy search utility
`Nextstep_backend/ai/json_cache.py` | New — JSON file persistence
`Nextstep_backend/core/management/commands/seed_careers.py` | New — seed command
`Nextstep-frontend/.../CareerBank.jsx` | Add AI search fallback + fuzzy search
`Nextstep-frontend/.../CareerBank.css` | Add loading states styles
### Docker
*Not needed.*  
SQLite + Django `locmem` cache is sufficient for development. Redis can be added later for production.

---

### Verification Checklist
1. Run `python manage.py makemigrations && migrate` → confirm new model
2. Run `python manage.py seed_careers` → confirm `Career` table populated
3. Call `POST /api/ai/search/` with a query not in JSON → verify Gemini response saved to cache, DB, and JSON file
4. Call same query again → verify cache hit, no Gemini call
5. Test frontend: search for a career not in static JSON → verify AI fallback triggers and result displays
6. Run existing tests: `python manage.py test`
