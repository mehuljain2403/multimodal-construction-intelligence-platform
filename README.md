# Multimodal Construction Intelligence Platform

A full-stack starter project for construction decision support with a React + Vite frontend and FastAPI backend.

## Features
- Construction site safety review from text and optional images
- Structural crack observation and preliminary analysis
- Real-estate valuation estimate
- Construction planning and material/cost estimation
- Daily site assistant and weather-aware advisory (weather is not live unless you connect a weather provider)
- Construction knowledge Q&A
- Strict Pydantic response models and a deterministic demo mode
- Upload validation, request validation, and user-facing error states

> **Important:** This is a decision-support prototype, not a substitute for a qualified engineer, safety officer, surveyor, or licensed property valuer. Image-based findings can be wrong. Do not use generated results as the sole basis for safety-critical decisions.

## Requirements
- Python 3.9+
- Node.js 18+
- npm
- Optional: an API key for a multimodal model provider

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; on macOS/Linux use: cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000/docs` for interactive API docs.

### 2. Frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite, normally `http://localhost:5173`.

## AI provider setup
The app runs in deterministic demo mode if `OPENAI_API_KEY` is not configured. To enable model-backed text analysis, add your key to `backend/.env`:
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```
The backend sends text and, when supplied, a resized/encoded image to the configured OpenAI Responses API. Keep secrets on the backend; never put API keys in React environment variables. Verify the model available to your account before use.

## Project structure
```text
backend/
  app/main.py
  app/schemas.py
  app/ai_service.py
  requirements.txt
  .env.example
frontend/
  src/App.jsx
  src/main.jsx
  src/styles.css
  index.html
  package.json
```

## API
- `GET /api/health`
- `POST /api/analyze` multipart form fields: `mode`, `prompt`, optional `image`, optional `project_data` (JSON string)
- `GET /docs`

`mode` values: `safety`, `crack`, `valuation`, `planning`, `daily_assistant`, `knowledge`.

## Current limitations / next steps
- No authentication, persistent database, audit log, or cloud deployment is configured.
- Valuation is a rough estimate based on user-provided assumptions; connect local market data for real use.
- Weather advisories are general unless a weather API is integrated.
- Crack analysis cannot determine structural safety from a photograph. Escalate concerning cracks to a qualified structural engineer.
- Add automated tests, rate limiting, malware scanning for uploads, storage retention rules, and deployment secrets before public deployment.
