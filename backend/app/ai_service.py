import base64
import json
import os
from io import BytesIO
from typing import Optional

from PIL import Image, UnidentifiedImageError
from google import genai
from google.genai import types

from .schemas import AnalysisResponse


MODES = {
    "safety": (
        "Review the supplied construction-site description/image for visible safety "
        "hazards and PPE concerns. Do not claim certainty from an image. "
        "Return practical mitigations."
    ),
    "crack": (
        "Describe visible crack observations, possible non-diagnostic causes, "
        "documentation steps, and when to escalate. Never declare a structure safe from a photo."
    ),
    "valuation": (
        "Give a rough real-estate valuation framework based only on supplied inputs. "
        "State assumptions and uncertainty. Do not invent local comparable sales."
    ),
    "planning": (
        "Create a practical preliminary construction plan with sequencing, dependencies, "
        "risks, and cost/material assumptions where data supports them."
    ),
    "daily_assistant": (
        "Give a concise daily site briefing with actions, weather caveats, coordination "
        "items, and safety reminders. Do not claim live weather access."
    ),
    "knowledge": (
        "Answer the construction question clearly, distinguishing general guidance "
        "from project-specific professional advice."
    ),
}


def _demo(mode: str, prompt: str, project_data: dict) -> dict:
    """Return a fallback response when GEMINI_API_KEY is not configured."""

    estimate = None

    if mode == "safety":
        summary = "Preliminary safety checklist generated in demo mode."
        findings = [
            {
                "title": "Site review required",
                "severity": "unknown",
                "description": (
                    "Demo mode cannot inspect or verify hazards. Review access routes, "
                    "edge protection, housekeeping, electrical safety, lifting zones, "
                    "and required PPE."
                ),
                "recommendation": (
                    "Have the site safety officer complete and record an on-site "
                    "inspection before work proceeds."
                ),
            }
        ]
        recommendations = [
            "Verify helmets, high-visibility clothing, eye protection, gloves, and task-specific PPE.",
            "Barricade openings and edges; keep walkways clear.",
            "Stop work and escalate any imminent danger.",
        ]

    elif mode == "crack":
        summary = "Preliminary crack documentation guidance generated in demo mode."
        findings = [
            {
                "title": "Crack assessment needed",
                "severity": "unknown",
                "description": (
                    "A photo or short description alone cannot establish cause, depth, "
                    "progression, or structural safety."
                ),
                "recommendation": (
                    "Record location, width, length, orientation, date, and change over time. "
                    "Consult a qualified structural engineer for significant or growing cracks."
                ),
            }
        ]
        recommendations = [
            "Photograph the crack with a scale and repeat from the same angle.",
            "Check for water ingress, displacement, and continuing movement.",
            (
                "Restrict access and seek urgent professional assessment if there is "
                "sudden widening, displacement, falling material, or other signs of distress."
            ),
        ]

    elif mode == "valuation":
        area = project_data.get("area_sqft")
        rate = project_data.get("rate_per_sqft")
        currency = project_data.get("currency", "INR")

        if (
            isinstance(area, (int, float))
            and not isinstance(area, bool)
            and isinstance(rate, (int, float))
            and not isinstance(rate, bool)
            and area > 0
            and rate > 0
        ):
            base = area * rate
            estimate = {
                "currency": currency,
                "low": round(base * 0.9, 2),
                "high": round(base * 1.1, 2),
                "assumptions": [
                    "Calculated from user-provided area multiplied by rate per square foot.",
                    "The ±10% range is illustrative and is not a market valuation.",
                ],
            }
        else:
            estimate = {
                "currency": currency,
                "assumptions": [
                    "Provide area_sqft and rate_per_sqft for an illustrative estimate.",
                    "Local comparable transactions and property condition are not included.",
                ],
            }

        summary = "Illustrative valuation framework; not a certified valuation."
        findings = []
        recommendations = [
            "Compare recent transactions for similar nearby properties.",
            "Adjust for location, age, condition, floor, amenities, title, and market conditions.",
            "Use a qualified local valuer for lending, legal, or transaction decisions.",
        ]

    elif mode == "planning":
        summary = (
            "Preliminary plan generated in demo mode. Tailor durations and quantities "
            "to the actual drawings and site."
        )
        findings = [
            {
                "title": "Scope and dependencies",
                "severity": "medium",
                "description": (
                    "A reliable schedule needs drawings, quantities, site constraints, "
                    "approvals, and crew/productivity assumptions."
                ),
                "recommendation": (
                    "Confirm scope and quantities before committing cost or dates."
                ),
            }
        ]
        recommendations = [
            "1. Confirm drawings, permits, BOQ, site survey, and utility locations.",
            "2. Plan procurement and long-lead materials.",
            "3. Sequence foundation, structure, envelope, MEP, finishes, and inspections.",
            "4. Assign owners, dependencies, safety controls, and contingency.",
        ]

    elif mode == "daily_assistant":
        summary = (
            "General daily site briefing generated in demo mode. "
            "No live weather feed is connected."
        )
        findings = []
        recommendations = [
            "Conduct a toolbox talk and confirm task-specific PPE.",
            "Review deliveries, workforce, equipment checks, permits, and high-risk activities.",
            "Check an authoritative local forecast before weather-sensitive work.",
            "Record blockers, incidents, inspections, and end-of-day progress.",
        ]

    else:
        summary = "Construction knowledge response generated in demo mode."
        findings = []
        recommendations = [
            "Share the project type, stage, location, constraints, and measurements for a more specific answer.",
            "Verify code, permit, and engineering requirements with the relevant local authority or qualified professional.",
        ]

    return {
        "mode": mode,
        "summary": summary,
        "findings": findings,
        "recommendations": recommendations,
        "estimate": estimate,
        "limitations": [
            "Demo mode: no AI model was called.",
            "Not a substitute for qualified professional assessment.",
        ],
        "source": "demo",
    }


def _image_part(image_bytes: bytes) -> types.Part:
    """Validate and resize an uploaded image for Gemini."""

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            image.thumbnail((1280, 1280))

            output = BytesIO()
            image.save(output, format="JPEG", quality=82, optimize=True)

            jpeg_bytes = output.getvalue()

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(
            "The uploaded file is not a valid supported image."
        ) from exc

    return types.Part.from_bytes(
        data=jpeg_bytes,
        mime_type="image/jpeg",
    )


def _response_schema() -> dict:
    """Define the JSON response structure expected from Gemini."""

    return {
        "type": "OBJECT",
        "properties": {
            "mode": {
                "type": "STRING",
                "enum": list(MODES.keys()),
            },
            "summary": {
                "type": "STRING",
            },
            "findings": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "severity": {
                            "type": "STRING",
                            "enum": [
                                "low",
                                "medium",
                                "high",
                                "critical",
                                "unknown",
                            ],
                        },
                        "description": {"type": "STRING"},
                        "recommendation": {"type": "STRING"},
                    },
                    "required": [
                        "title",
                        "severity",
                        "description",
                        "recommendation",
                    ],
                },
            },
            "recommendations": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
            },
            "estimate": {
                "type": "OBJECT",
                "nullable": True,
                "properties": {
                    "currency": {"type": "STRING"},
                    "low": {"type": "NUMBER", "nullable": True},
                    "high": {"type": "NUMBER", "nullable": True},
                    "assumptions": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                    },
                },
                "required": ["currency", "assumptions"],
            },
            "limitations": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
            },
            "source": {
                "type": "STRING",
                "enum": ["ai", "demo"],
            },
        },
        "required": [
            "mode",
            "summary",
            "findings",
            "recommendations",
            "estimate",
            "limitations",
            "source",
        ],
    }


def analyze(
    mode: str,
    prompt: str,
    project_data: dict,
    image_bytes: Optional[bytes] = None,
    content_type: str = "image/jpeg",
) -> AnalysisResponse:
    """Analyze construction information using Gemini."""

    if mode not in MODES:
        raise ValueError(f"Unsupported analysis mode: {mode}")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    # Preserve demo functionality when no Gemini key is configured.
    if not api_key:
        return AnalysisResponse.model_validate(
            _demo(mode, prompt, project_data)
        )

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    ).strip()

    if not model_name:
        model_name = "gemini-2.5-flash"

    client = genai.Client(api_key=api_key)

    user_text = (
        f"Task: {MODES[mode]}\n"
        f"User description/question: {prompt or '(none supplied)'}\n"
        f"Structured project data (JSON): "
        f"{json.dumps(project_data, ensure_ascii=False, default=str)}\n\n"
        "Return a JSON object matching the provided response schema. "
        "The mode must match the requested mode. Severity must be low, medium, "
        "high, critical, or unknown. Do not invent facts, measurements, prices, "
        "code requirements, or local comparable sales. State uncertainty. "
        "For construction safety and cracks, do not declare a site or structure "
        "safe from an image. Keep recommendations practical. Set source to 'ai'."
    )

    contents = [user_text]

    if image_bytes:
        contents.append(_image_part(image_bytes))

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_response_schema(),
            temperature=0.2,
        ),
    )

    response_text = getattr(response, "text", None)

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty response. Check the API configuration and retry."
        )

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON. Please retry the request."
        ) from exc

    # Enforce server-controlled fields.
    result["mode"] = mode
    result["source"] = "ai"

    result.setdefault("findings", [])
    result.setdefault("recommendations", [])
    result.setdefault("estimate", None)
    result.setdefault("limitations", [])

    result["limitations"] = list(result["limitations"]) + [
        "AI-generated result; verify findings on site with qualified personnel."
    ]

    return AnalysisResponse.model_validate(result)