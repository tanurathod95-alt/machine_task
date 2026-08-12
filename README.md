# Student Records API

A FastAPI-based REST service for managing student records, secured with JWT authentication and backed by PostgreSQL. Source data is migrated from `Student_Records.xlsx` into a PostgreSQL database.

## Features

- 🔐 JWT-based authentication (register/login, protected routes)
- 🗄️ PostgreSQL database via SQLAlchemy ORM
- 📥 One-time migration script to load Excel data into PostgreSQL
- 📚 Auto-generated interactive docs (Swagger UI / ReDoc)
- ✅ Request/response validation via Pydantic
- 🔎 Filtering, search, and aggregate statistics on student data

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Server | Uvicorn |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose) + password hashing (passlib/bcrypt) |
| Validation | Pydantic |
| Data Source | openpyxl (reads the Excel file for migration) |

## Project Structure

```
student_api/
├── main.py                # FastAPI app instance, route registration
├── database.py             # SQLAlchemy engine/session, PostgreSQL connection
├── models.py                # SQLAlchemy ORM models (Student, User)
├── schemas.py                # Pydantic request/response schemas
├── auth.py                    # JWT creation/verification, password hashing
├── crud.py                     # Database operations for students
├── routers/
│   ├── auth_routes.py           # /auth endpoints
│   └── student_routes.py        # /students endpoints
├── migrate_excel_to_pg.py         # Script: loads Student_Records.xlsx into PostgreSQL
├── requirements.txt
├── .env.example
└── README.md
```

## Data Source

`Student_Records.xlsx` — 100 records with columns:

| Column | Type |
|---|---|
| Student ID | string |
| First Name | string |
| Last Name | string |
| Class | integer |
| Section | string |
| Stream | string |
| City | string |
| Attendance (%) | integer |

This file is read once by `migrate_excel_to_pg.py` and inserted into the `students` table in PostgreSQL.

## API Endpoints (10 total)

### Auth (public)

| # | Method | Endpoint | Description |
|---|---|---|---|
| 1 | POST | `/auth/register` | Create a new user account |
| 2 | POST | `/auth/login` | Authenticate and receive a JWT access token |

### Students (JWT-protected — requires `Authorization: Bearer <token>`)

| # | Method | Endpoint | Description |
|---|---|---|---|
| 3 | GET | `/students` | List students (pagination + filter by class/section/stream/city) |
| 4 | GET | `/students/{student_id}` | Get a single student by ID |
| 5 | POST | `/students` | Create a new student record |
| 6 | PUT | `/students/{student_id}` | Update a student record (full update) |
| 7 | PATCH | `/students/{student_id}` | Partially update a student record |
| 8 | DELETE | `/students/{student_id}` | Delete a student record |
| 9 | GET | `/students/search?name=` | Search students by first/last name |
| 10 | GET | `/students/stats` | Aggregate stats (avg attendance, counts per class/stream) |

## Setup

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+ running locally or remotely

### 2. Clone & install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-multipart
openpyxl
python-dotenv
```

### 3. Configure environment

Copy `.env.example` to `.env` and set:

```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/student_db
SECRET_KEY=<your-jwt-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Create the database

```bash
createdb student_db
```

### 5. Migrate Excel data into PostgreSQL

```bash
python migrate_excel_to_pg.py
```

This reads `Student_Records.xlsx`, creates the `students` table (if not present), and inserts all 100 rows.

### 6. Run the API

```bash
uvicorn main:app --reload
```

- API base URL: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication Flow

1. `POST /auth/register` — create a user with `username` and `password`.
2. `POST /auth/login` — submit credentials, receive a JWT `access_token`.
3. Include the token on all `/students` requests:
   ```
   Authorization: Bearer <access_token>
   ```
4. Requests without a valid token receive `401 Unauthorized`.

## Example Requests

**Register**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass123"}'
```

**Login**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePass123"}'
```

**List students (authenticated)**
```bash
curl http://127.0.0.1:8000/students \
  -H "Authorization: Bearer <access_token>"
```

## Notes

- Passwords are hashed (never stored in plain text).
- JWT tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.
- The migration script is idempotent-safe when run against an empty table; re-running against a populated table will duplicate rows unless a uniqueness constraint on `Student ID` is enforced (recommended).