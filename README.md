# CEIT CMS Backend

> **⚠️ WARNING: DO NOT PUSH DIRECTLY TO THE MAIN BRANCH ⚠️**
>
> Always create a feature branch and submit a pull request for review.

---

## Project Structure

```
ceit-cms-backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration template
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       │   └── auth.py
│   │       ├── dependencies.py # Dependency injection
│   │       └── router.py       # API router
│   ├── core/
│   │   ├── config.py           # App configuration
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Auth & security utils
│   ├── middleware/
│   │   └── cors.py             # CORS middleware
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── base.py
│   │   ├── permission.py
│   │   ├── role.py
│   │   └── user.py
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── main.py                 # FastAPI app entry point
├── scripts/
│   └── seed.py                 # Database seeding script
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment variables
├── alembic.ini                 # Alembic configuration
└── requirements.txt            # Python dependencies
```

---

## Setup Guide

### 1. Create Virtual Environment

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Copy the example env file and configure it:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials and secrets.

### 4. Database Migrations

**Create a new migration:**

```bash
# Linux/macOS
alembic revision --autogenerate -m "Migration message"

# Windows
alembic revision --autogenerate -m "Migration message"
```

**Apply migrations:**

```bash
alembic upgrade head
```

**Rollback last migration:**

```bash
alembic downgrade -1
```

### 5. Seed Database

```bash
python scripts/seed.py
```

### 6. Run Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

---

## Cloudinary Uploads (Notes for Next Dev)

### Environment variables

Configured via Pydantic `Settings` in `app/core/config.py`.

- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `CLOUDINARY_FOLDER` (optional default folder/prefix for uploads)

If Cloudinary vars are missing, the API will still start, but upload requests will return `500` with a clear “missing env vars” message.

### Endpoint

- `POST /api/v1/uploads/` (authenticated)
	- Content-Type: `multipart/form-data`
	- Form field: `file`
	- Optional query params: `folder`, `public_id`

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/uploads/?folder=articles" \
	-H "Authorization: Bearer <ACCESS_TOKEN>" \
	-F "file=@./path/to/image.jpg"
```

### Implementation pointers

- Upload logic lives in `app/services/upload_service.py`.
- The Cloudinary SDK call is synchronous, so the route runs it via `run_in_threadpool` to avoid blocking the event loop.
- Today the route requires authentication (`require_auth`). If you want permission-based access, swap to `require_permission("media.upload")` and add that permission to your seed/migrations.
