# NextStep Navigator — Project Documentation

> **Project Name:** NextStep Navigator (a.k.a. PathSeeker)  
> **Type:** Full-stack career guidance web application  
> **Stack:** Django + Django REST Framework (backend), React + Vite + Bootstrap (frontend), Google Gemini (AI)  

---

## 1. Overview

NextStep Navigator is an responsive, interactive career-passport platform that helps students, graduates, and working professionals make informed career decisions. It offers role-based personalization, an interest quiz, an AI-assisted career bank, a resource library, multimedia guidance, success stories, feedback, and admin controls.

The repository is organized as a monorepo with two main folders:

```
Nextstep-with-backend/
├── Nextstep_backend/   # Django REST API
├── Nextstep-frontend/  # React + Vite SPA
└── documentation.md    # This file
```

---

## 2. Folder Structure

```text
Nextstep-with-backend/
├── Nextstep_backend/                 # Django project root
│   ├── nextstep/                   # Project configuration
│   │   ├── settings.py             # Django settings, CORS, JWT, email, cache
│   │   ├── urls.py                 # Root URL routing
│   │   ├── asgi.py                 # ASGI entry point
│   │   └── wsgi.py                 # WSGI entry point
│   ├── accounts/                   # Authentication & user management app
│   │   ├── models.py               # Custom User model with role field
│   │   ├── views.py                # Register, login, logout, password reset/change, profile
│   │   ├── serializers.py          # User, register, password serializers
│   │   ├── urls.py                 # Auth routes
│   │   └── authentication.py       # Authentication helpers
│   ├── core/                       # Main domain logic
│   │   ├── models.py               # Career, Resource, Multimedia, SuccessStory, Quiz, Feedback, UserProfile, Interaction, Tag, Skill
│   │   ├── views.py                # DRF viewsets for all core models
│   │   ├── serializers.py          # Serializers for core models
│   │   ├── urls.py                 # Core API routes
│   │   ├── admin.py                # Django admin configuration
│   │   └── management/commands/    # Custom management commands (seed_careers, populate_questions, etc.)
│   ├── ai/                         # AI/Gemini integration
│   │   ├── gemini.py               # Gemini client prompts & structured output
│   │   ├── views.py                # AI endpoints (recommendations, search, resource library)
│   │   ├── models.py               # AIRecommendation cache model
│   │   ├── search.py               # Fuzzy search over static career/resource data
│   │   ├── json_cache.py           # JSON persistence utilities
│   │   └── urls.py                 # AI routes
│   ├── fixtures/                   # Static data fixtures
│   ├── media/                      # Uploaded files (resources, profiles, multimedia, success stories)
│   ├── templates/                  # HTML email templates
│   ├── manage.py                   # Django management entry point
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables (not committed)
│
├── Nextstep-frontend/              # Frontend workspace
│   └── nextstep-navigator/         # React app
│       ├── src/
│       │   ├── App.jsx             # Root component with routing
│       │   ├── main.jsx            # React entry point
│       │   ├── index.css           # Global styles
│       │   ├── components/         # Page/section components (Home, CareerBank, Quiz, etc.)
│       │   ├── pages/auth/         # Login, Register, ForgotPassword, Profile, ProfileSetting
│       │   ├── context/            # React context (ProfileContext)
│       │   ├── hooks/              # Custom React hooks
│       │   ├── utils/              # API client, auth helpers, Lottie preload
│       │   ├── data/               # Static JSON data (careerData.json, menuData.json, etc.)
│       │   └── assets/             # Images, animations, logos
│       ├── package.json            # Node dependencies & scripts
│       └── vite.config.js          # Vite configuration with path aliases
│
├── .gitignore
├── README.md                       # Short project readme (placeholder)
├── SRS.md                          # Software Requirements Specification
├── issues.md                       # Project status, gaps, and action items
├── DjangoRunServer.bat             # Quick Windows launcher for backend
└── ReactRunServer.bat              # Quick Windows launcher for frontend
```

---

## 3. Tech Stack

### Backend
- **Django 5.2.x** — Web framework
- **Django REST Framework 3.16.x** — REST API
- **djangorestframework-simplejwt 5.5.x** — JWT authentication with token blacklist
- **django-cors-headers 4.9.x** — CORS handling
- **django-filter 25.1.x** — Query filtering
- **django-jazzmin 3.0.x** — Enhanced Django admin theme
- **SQLite 3** — Default development database
- **SendGrid SMTP** — Email delivery (configurable)
- **Google Gemini API** — AI career recommendations and search

### Frontend
- **React 19.1.x** — UI library
- **Vite 7.1.x** — Build tool and dev server
- **Bootstrap 5.3.x** + **React-Bootstrap** — Styling and UI components
- **Axios** — HTTP client
- **React Router DOM 7.9.x** — Client-side routing
- **Framer Motion** — Animations
- **Lottie React** — Lottie animations
- **Chart.js + react-chartjs-2** — Data visualization
- **Lucide React + React Icons** — Icon libraries

### AI / External Services
- **Google Gemini 2.5 Flash** — LLM for recommendations, search, and resource generation
- **SendGrid** — Transactional email (password reset, etc.)

---

## 4. Features

### Implemented

1. **Authentication & User Management**
   - Role-based registration (Student, Graduate, Professional)
   - JWT login/logout with token refresh and blacklisting
   - User profile read/update with image upload
   - Change password
   - Password reset via email link (uid + token)

2. **Career Bank**
   - Browse/search/filter careers by domain, tags, and skills
   - Career detail view with AI-generated insights, related careers, and video resources
   - Static JSON fallback plus AI-generated search fallback

3. **AI-Powered Interest Quiz**
   - Multi-step quiz stored in backend
   - AI generates 3 personalized career recommendations based on responses
   - Results cached in Django cache + database

4. **Resource Library**
   - Curated documents, guides, PDFs
   - AI-generated resource collections
   - File upload support via backend

5. **Multimedia Guidance**
   - Video, audio, image, article content
   - Backend models support transcripts, ratings, and tagging

6. **Success Stories**
   - User-submitted success stories
   - Admin approval workflow
   - Domain-based filtering

7. **Feedback & Contact**
   - Categorized feedback (bug, suggestion, query, other)
   - Backend status tracking

8. **Admin Panel**
   - Jazzmin-themed Django admin
   - Model management for careers, resources, multimedia, quizzes, feedback, success stories
   - Admin actions to approve stories and rebuild content text

9. **Interaction Tracking**
   - Generic interaction model (view, like, save, apply, share, dismiss)
   - Can be attached to any content type

### In Progress / Partial

- Full-text/semantic search (currently DRF filters + fuzzy matching)
- ElasticSearch integration
- Collaborative filtering recommendations
- Video player with transcript toggle, playback controls, related suggestions
- Admin analytics dashboard
- Docker / deployment automation

---

## 5. Architecture

### Backend Architecture

The backend follows Django's app-based architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                         Django REST API                     │
├─────────────┬─────────────┬─────────────────┬───────────────┤
│  accounts   │    core     │       ai        │     admin     │
│  (auth)     │  (domain)   │  (Gemini LLM)   │  (Jazzmin)    │
└─────────────┴─────────────┴─────────────────┴───────────────┘
│                        PostgreSQL/SQLite                    │
└─────────────────────────────────────────────────────────────┘
```

**Key design patterns:**
- DRF `ModelViewSet` for CRUD endpoints
- Custom permission classes (`IsOwnerOrReadOnly`)
- Scoped throttling for auth and AI endpoints
- Generic relations for interaction tracking
- Denormalized `content_text` fields for future search/embedding
- Three-tier AI response caching (Django cache → DB → Gemini API)

### Frontend Architecture

The frontend is a single-page React application:

```
┌────────────────────────────────────────────┐
│              React + Vite SPA                │
├────────────────────────────────────────────┤
│  React Router (BrowserRouter)                │
│  ProfileContext (global user state)          │
│  Axios interceptors (JWT refresh)              │
├────────────────────────────────────────────┤
│  Pages:                                        │
│    Home, CareerBank, Quiz, Multimedia,       │
│    Resources, SuccessStories, About,         │
│    Contact, Profile, ProfileSetting          │
├────────────────────────────────────────────┤
│  Auth Pages: Login, Register,                │
│  ForgotPassword, ResetPasswordConfirm        │
└────────────────────────────────────────────┘
```

---

## 6. API Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Obtain JWT access/refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/token/verify/` | Verify access token |
| GET | `/api/auth/profile/` | Get current user profile |
| PATCH | `/api/auth/profile/update/` | Update user profile |
| POST | `/api/auth/password/change/` | Change password |
| POST | `/api/auth/password/reset/` | Request password reset email |
| POST | `/api/auth/password/reset/confirm/` | Confirm password reset |
| POST | `/api/auth/logout/` | Blacklist refresh token |

### Core (`/api/core/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| CRUD | `/api/core/tags/` | Tags |
| CRUD | `/api/core/skills/` | Skills |
| CRUD | `/api/core/careers/` | Career bank |
| CRUD | `/api/core/resources/` | Resource library |
| CRUD | `/api/core/multimedia/` | Multimedia content |
| CRUD | `/api/core/success-stories/` | Success stories |
| CRUD | `/api/core/feedback/` | Feedback submissions |
| CRUD | `/api/core/quizzes/` | Quizzes |
| CRUD | `/api/core/quiz-questions/` | Quiz questions |
| CRUD | `/api/core/quiz-attempts/` | Quiz attempts |
| CRUD | `/api/core/interactions/` | User interactions |
| GET/PATCH | `/api/core/profile/` | User profile (core) |

### AI (`/api/ai/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/recommend/` | Quiz-based career recommendations |
| POST | `/api/ai/recommend-detail/` | Per-career detail recommendation |
| POST | `/api/ai/search/` | Free-text career search |
| POST | `/api/ai/resources/generate/` | Generate resource library |
| POST | `/api/ai/resources/search/` | Search resources |

---

## 7. Environment Variables

Create a `.env` file inside `Nextstep_backend/` with at least:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=your-verified-sender@example.com
FRONTEND_URL=http://localhost:5173
```

Create a `.env` file inside `Nextstep-frontend/nextstep-navigator/` with:

```env
VITE_API_URL=http://localhost:8000/api
```

---

## 8. Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

```bash
cd Nextstep_backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Default backend URL: `http://localhost:8000`

### Frontend Setup

```bash
cd Nextstep-frontend/nextstep-navigator

# Install dependencies
npm install

# Run dev server
npm run dev
```

Default frontend URL: `http://localhost:5173`

### Quick Launch (Windows)

Use the provided batch files:

```bash
DjangoRunServer.bat
ReactRunServer.bat
```

---

## 9. Running the Project

1. Start the backend server (`python manage.py runserver`).
2. Start the frontend dev server (`npm run dev`).
3. Open `http://localhost:5173` in your browser.
4. Register a new account or log in.
5. Explore career paths, take the quiz, and browse resources.

---

## 10. Database Schema Overview

### `accounts.User`
- `id`, `username`, `email`, `first_name`, `last_name`
- `role`: student / graduate / professional
- `bio`

### `core.Tag`
- `name`, `slug`

### `core.Skill`
- `name`

### `core.Career`
- `domain`, `title`, `description`
- `required_skills` (M2M to Skill)
- `education_path`, `expected_salary`
- `tags` (M2M to Tag)
- `popularity`, `content_text`, `embedding_id`
- `created_at`, `updated_at`

### `core.Resource`
- `title`, `category`, `description`, `file`
- `tags`, `views_count`, `created_by`, `created_at`
- `content_text`, `embedding_id`

### `core.Multimedia`
- `title`, `type`, `url`, `uploaded_file`
- `tags`, `transcript`, `rating_avg`, `rating_count`
- `created_by`, `created_at`, `content_text`, `embedding_id`

### `core.SuccessStory`
- `title`, `domain`, `story_text`, `image`
- `submitted_by`, `approved_by`, `approved_at`
- `submitted_at`, `is_approved`, `content_text`, `embedding_id`

### `core.UserProfile`
- `user` (1-to-1 with User)
- `education_level`, `interests` (M2M to Tag)
- `profile_image`, `bio`, `updated_at`

### `core.Feedback`
- `user`, `category`, `message`, `status`, `submitted_at`, `handled_by`

### `core.Quiz`, `core.QuizQuestion`, `core.QuizAttempt`
- Quiz framework with questions, options, and user attempts stored as JSON

### `core.Interaction`
- Generic relation to record user events on any content type
- `interaction_type`: view, like, save, apply, share, dismiss

### `ai.AIRecommendation`
- Caches AI responses by input hash
- `recommendation_type`: quiz / career_detail / search
- `input_hash`, `input_data`, `output_data`, `created_at`, `accessed_at`

---

## 11. AI Integration

The `ai` app uses Google's Gemini API to provide:

1. **Career Recommendations** — Based on quiz answers, returns 3 careers with reasons.
2. **Career Detail Insights** — Given a career, returns a recommendation, related career, and YouTube embed URL.
3. **Career Search** — Free-text search with fallback to AI-generated structured career data.
4. **Resource Library Generation** — Generates curated resources for a given topic.

### Caching Strategy

AI responses are cached using a three-tier approach:

1. **Django Cache** (fastest, in-memory) — keyed by `ai:<type>:<input_hash>`
2. **AIRecommendation Model** (durable fallback) — persists in SQLite
3. **Gemini API** — called only on cache miss

This reduces API costs and improves response times.

### Fuzzy Search

The `ai/search.py` module uses `difflib.get_close_matches` to match user queries against static JSON career and resource data, tolerating minor typos and misspellings before falling back to Gemini.

---

## 12. Security Considerations

- JWT tokens stored in `localStorage` on the frontend
- Password reset uses Django's token generator and uidb64 encoding
- CORS restricted to local development origins
- Scoped throttling on auth and AI endpoints
- Environment variables for secrets (`SECRET_KEY`, `GEMINI_API_KEY`, `EMAIL_HOST_PASSWORD`)
- Password validators enabled via Django

> **Note:** Review `issues.md` for known security gaps, including the token blacklist app configuration and production hardening recommendations.

---

## 13. Testing

Run backend tests with:

```bash
cd Nextstep_backend
python manage.py test
```

Frontend linting:

```bash
cd Nextstep-frontend/nextstep-navigator
npm run lint
```

---

## 14. Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure Redis for caching and sessions
- [ ] Enable HTTPS and secure cookies:
  - `SECURE_SSL_REDIRECT`
  - `SESSION_COOKIE_SECURE`
  - `CSRF_COOKIE_SECURE`
- [ ] Configure SendGrid or another email backend
- [ ] Add proper logging and monitoring
- [ ] Set up CI/CD pipeline
- [ ] Run collectstatic and configure a web server (Nginx) / WSGI server (Gunicorn)
- [ ] Review and tune DRF throttling rates
- [ ] Add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS` if not already present

---

## 15. Known Issues & Next Steps

See `issues.md` for a detailed project status report. High-priority items include:

1. Fix JWT token blacklist app registration
2. Harden auth and AI endpoint rate limiting
3. Add robust fallback/error handling for Gemini API
4. Implement full-text/semantic search (ElasticSearch or vector DB)
5. Complete frontend integration for quizzes, multimedia player, and admin analytics
6. Add unit and integration tests
7. Add Docker and deployment automation

---

## 16. References

- `SRS.md` — Software Requirements Specification
- `issues.md` — Project status and actionable next steps
- `Nextstep-frontend/docs/NextStep Navigator Documentation.pdf` — Additional frontend documentation
- `Nextstep_backend/AI_Career_Plan.md` — AI caching and search enhancement plan

---

*Last updated: August 24, 2026*
