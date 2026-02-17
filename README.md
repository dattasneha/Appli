# Appli

A job application portal API built with FastAPI, SQLModel, and PostgreSQL.

**Live API**: https://appli-oc5h.onrender.com/docs

**Frontend**: https://appli-frontend.onrender.com

## Features

- **User Authentication**: Register and login with JWT-based authentication
- **Role-Based Access Control**: Separate permissions for users and admins
- **Job Management**: Admins can create, delete, and toggle job listings
- **Application System**: Users can apply to jobs and track their applications
- **Application Status Tracking**: Status history for applications (submitted, shortlisted, approved, rejected)

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (async with asyncpg)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: PBKDF2-HMAC-SHA256
- **Server**: Uvicorn / Gunicorn
- **Python**: 3.11.9

## Project Structure

```
src/
├── __init__.py         # FastAPI app initialization and router setup
├── config.py           # Environment configuration (Pydantic Settings)
├── dependency.py       # JWT authentication dependency
├── main.py             # Application entry point
├── model.py            # SQLModel database models
├── auth/
│   ├── routes.py       # Login and registration endpoints
│   └── util.py         # Password hashing and JWT utilities
├── db/
│   └── main.py         # Database engine and initialization
└── jobs/
    ├── admin_routes.py # Admin-only job and application management
    └── user_routes.py  # User job browsing and application endpoints
```

## API Endpoints

### Authentication

| Method | Endpoint             | Description                   |
| ------ | -------------------- | ----------------------------- |
| POST   | `/appli/v1/login`    | Login with email and password |
| POST   | `/appli/v1/register` | Register a new user account   |

### Jobs (User)

| Method | Endpoint                        | Description                    |
| ------ | ------------------------------- | ------------------------------ |
| GET    | `/appli/v1/jobs`                | List all active jobs           |
| GET    | `/appli/v1/jobs/{job_id}`       | Get a specific job             |
| POST   | `/appli/v1/jobs/apply/{job_id}` | Apply to a job (auth required) |

### Applications (User)

| Method | Endpoint                         | Description                                |
| ------ | -------------------------------- | ------------------------------------------ |
| GET    | `/appli/v1/me/applications`      | List my applications (auth required)       |
| GET    | `/appli/v1/me/applications/{id}` | Get my application details (auth required) |

### Admin

| Method | Endpoint                                  | Description               |
| ------ | ----------------------------------------- | ------------------------- |
| POST   | `/appli/v1/admin/jobs`                    | Create a new job          |
| DELETE | `/appli/v1/admin/jobs/{job_id}`           | Delete a job              |
| PATCH  | `/appli/v1/admin/jobs/{job_id}/status`    | Toggle job active status  |
| GET    | `/appli/v1/admin/application`             | List all applications     |
| GET    | `/appli/v1/admin/application/{id}`        | Get application details   |
| PATCH  | `/appli/v1/admin/application/{id}/status` | Update application status |

## Data Models

### User Roles

- `user` - Regular user who can browse jobs and submit applications
- `admin` - Administrator who can manage jobs and review applications

### Application Status

- `submitted` - Initial status when application is created
- `shortlisted` - Application has been shortlisted for review
- `approved` - Application has been approved
- `rejected` - Application has been rejected

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Appli
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ACCESS_TOKEN_KEY=your-secret-key
   ```

5. **Run the application**

   ```bash
   python -m src.main
   ```

   The API will be available at `http://127.0.0.1:8000`

## API Documentation

Once running, access the interactive API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Usage Examples

### Register a new user

```bash
curl -X POST "http://127.0.0.1:8000/appli/v1/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "Pass123", "role": "user"}'
```

### Login

```bash
curl -X POST "http://127.0.0.1:8000/appli/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "Pass123"}'
```

### List jobs

```bash
curl -X GET "http://127.0.0.1:8000/appli/v1/jobs"
```

### Apply to a job (authenticated)

```bash
curl -X POST "http://127.0.0.1:8000/appli/v1/jobs/apply/{job_id}?resume_url=https://example.com/resume.pdf" \
  -H "Authorization: Bearer <your_token>"
```

## Deployment

The application is configured for deployment on Render with:

- `runtime.txt` - Specifies Python 3.11.9
- `gunicorn` - Production WSGI server
