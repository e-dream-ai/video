# AGENT.md — video

## Overview
Video processing service. Generates thumbnails, filmstrips, and handles video transcoding for dream content.

## Stack
- **Runtime:** Python 3.12
- **Framework:** Flask
- **Queue:** Redis + RQ (Redis Queue)
- **Dependencies:** FFmpeg (system), requests, marshmallow
- **Server:** Gunicorn (production)

## Project Structure
```
app.py           # Flask app entry point
worker.py        # RQ worker entry point
api/             # Flask route blueprints
clients/         # External service clients
config.py        # App configuration
constants/       # Constants
decorators/      # Route decorators
schemas/         # Marshmallow serialization schemas
utils/           # Utility functions
python-api/      # Vendored edream_sdk
```

## Commands
```bash
pip install -r requirements.txt
flask run          # Start Flask dev server (port 5000)
python worker.py   # Start RQ worker (separate terminal)
```

## Key Patterns
- Flask blueprints in `api/` define REST endpoints
- RQ workers process video jobs asynchronously
- FFmpeg used for thumbnail extraction, filmstrip generation, and transcoding
- Uses edream_sdk (python-api) for backend API communication

## Deployment
Heroku — push to `stage` or `main` branch.
