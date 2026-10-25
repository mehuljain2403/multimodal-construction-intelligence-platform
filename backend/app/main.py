
import json
import os
from pathlib import Path
from typing import Optional
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError

from .ai_service import analyze
from .schemas import AnalysisResponse


# --------------------------------------------------
# Environment Configuration
# --------------------------------------------------

# Load backend/.env regardless of the current working directory.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Multimodal Construction Intelligence API",
    version="1.0.0",
    description=(
        "AI-powered construction intelligence API supporting safety analysis, "
        "crack assessment, valuation, planning, daily assistance, and knowledge queries."
    ),
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

origin = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Upload Configuration
# --------------------------------------------------

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "8"))
MAX_BYTES = MAX_UPLOAD_MB * 1024 * 1024

VALID_MODES = {
    "safety",
    "crack",
    "valuation",
    "planning",
    "daily_assistant",
    "knowledge",
}


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    """
    Check whether the backend is running and whether a Gemini API key
    is configured. This does not make a live request to Gemini.
    """

    gemini_configured = bool(
        os.getenv("GEMINI_API_KEY", "").strip()
    )

    return {
        "status": "ok",
        "ai_provider": "gemini",
        "ai_configured": gemini_configured,
    }


# --------------------------------------------------
# Construction Analysis Endpoint
# --------------------------------------------------

@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
)
async def run_analysis(
    mode: str = Form(...),
    prompt: str = Form(""),
    project_data: str = Form("{}"),
    image: Optional[UploadFile] = File(None),
):
    """
    Run a construction analysis using Gemini.

    Supported modes:
    - safety
    - crack
    - valuation
    - planning
    - daily_assistant
    - knowledge
    """

    # Validate analysis mode.
    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported analysis mode.",
        )

    # Validate prompt length.
    if len(prompt) > 12000:
        raise HTTPException(
            status_code=413,
            detail="Prompt is too long (maximum 12,000 characters).",
        )

    # Parse project data.
    try:
        data = json.loads(project_data or "{}")

        if not isinstance(data, dict):
            raise ValueError(
                "Project data must be a JSON object."
            )

    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="project_data must be a JSON object.",
        )

    # Initialize image variables.
    image_bytes = None
    content_type = "image/jpeg"

    # Validate and read an optional uploaded image.
    if image is not None:
        uploaded_content_type = image.content_type or ""

        if not uploaded_content_type.startswith("image/"):
            raise HTTPException(
                status_code=415,
                detail="Upload must be an image.",
            )

        try:
            image_bytes = await image.read(MAX_BYTES + 1)

        finally:
            await image.close()

        # Enforce maximum upload size.
        if len(image_bytes) > MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Image exceeds the {MAX_UPLOAD_MB} MB limit."
                ),
            )

        # Reject empty uploads.
        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        content_type = uploaded_content_type or "image/jpeg"

        # Verify that the uploaded bytes represent a readable image.
        try:
            with Image.open(BytesIO(image_bytes)) as uploaded_image:
                uploaded_image.verify()

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):
            raise HTTPException(
                status_code=415,
                detail="File is not a valid supported image.",
            )

    # Call the AI service.
    try:
        result = analyze(
            mode=mode,
            prompt=prompt,
            project_data=data,
            image_bytes=image_bytes,
            content_type=content_type,
        )

        return result

    except ValueError as exc:
        # Return validation errors without exposing internal details.
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the exception in the backend terminal for debugging.
        print(
            f"Analysis failed for mode '{mode}': "
            f"{type(exc).__name__}: {exc}"
        )

        # Keep internal provider errors out of the client response.
        raise HTTPException(
            status_code=502,
            detail=(
                "Analysis failed. Check backend logs and "
                "Gemini API configuration."
            ),
        ) from exc
