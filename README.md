# Tapai Ko Sathi

Clean project structure and core run instructions for local development.

## Quick Start

1. Copy environment file:

```powershell
copy .env.example .env
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the project:

```powershell
python manage.py migrate
python manage.py runserver
```

4. Open app:

```
http://127.0.0.1:8000
```

## Documentation

Detailed setup, API, deployment, and structure notes are maintained in:

- `docs/PROJECT_DOCUMENTATION.md`