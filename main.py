"""
Kestrel Prova API
FastAPI backend for Prova AI Governance Inspector.

Frontend -> FastAPI /audit -> Azure AI Foundry Kestrel workflow -> Prova JSON response.

Design choices:
- Fail fast if Foundry does not return valid Prova JSON.
- Same request/response schema as the current Prova frontend.
- Uses Managed Identity / DefaultAzureCredential.
"""

import json
import logging
import os
import re
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kestrel-prova-api")


# ── Configuration ────────────────────────────────────────────────────────────
AZURE_AI_PROJECT_ENDPOINT = os.getenv(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://anirops-kestrel-resource.services.ai.azure.com/api/projects/anirops-kestrel",
)

KESTREL_WORKFLOW_NAME = os.getenv(
    "KESTREL_WORKFLOW_NAME",
    "Kestrel-governance-engine",
)

KESTREL_WORKFLOW_VERSION = os.getenv(
    "KESTREL_WORKFLOW_VERSION",
    "5",
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "https://anir-a.github.io").split(",")
    if origin.strip()
]


# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kestrel Prova API",
    description="AI Governance Inspector backend powered by Azure AI Foundry Kestrel workflow",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


# ── Request / Response models ────────────────────────────────────────────────
class AuditRequest(BaseModel):
    agent_content: str = Field(..., description="AI use case, agent prompt, or system description")
    agent_type: str = "general"
    deploy_context: str = "internal-low"
    pillars: list[str] = []


class Finding(BaseModel):
    type: str
    text: str


class Pillar(BaseModel):
    id: str
    name: str
    score: int
    verdict: str
    au_ref: str = ""
    nist: str = ""
    summary: str
    findings: list[Finding]
    recommendation: str


class AuditResponse(BaseModel):
    overall_score: int
    verdict: str
    headline: str
    summary: str
    exec_summary: str
    gate_level: str
    gate_note: str
    non_negotiable_fails: list[str]
    pillars: list[Pillar]
    raw_text: str = ""


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "kestrel-prova-api",
        "workflow": KESTREL_WORKFLOW_NAME,
        "workflow_version": KESTREL_WORKFLOW_VERSION,
        "mode": "foundry-live",
    }


# ── Helpers ─────────────────────────────────────────────────────────────────
def build_kestrel_prompt(req: AuditRequest) -> str:
    """
    Keep the prompt simple. The workflow and orchestrator instructions do the real governance work.
    This prompt gives the workflow enough structured context.
    """
    selected_pillars = ", ".join(req.pillars) if req.pillars else "all applicable governance pillars"

    return f"""
Evaluate the following AI use case through the Kestrel Governance Engine.

AI use case / agent description:
{req.agent_content}

Agent type:
{req.agent_type}

Deployment context:
{req.deploy_context}

Requested governance focus:
{selected_pillars}

Return the final answer using the Prova JSON schema from the Kestrel Orchestrator instructions.
Return only valid JSON.
""".strip()


def extract_text_from_foundry_response(response: Any) -> str:
    """
    Azure AI Foundry response objects can vary slightly by SDK version.
    This function extracts the final text defensively.
    """

    # Common convenience property.
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    # Try dictionary conversion.
    response_dict = None
    if hasattr(response, "as_dict"):
        try:
            response_dict = response.as_dict()
        except Exception:
            response_dict = None

    if response_dict is None:
        try:
            response_dict = json.loads(json.dumps(response, default=str))
        except Exception:
            response_dict = None

    if isinstance(response_dict, dict):
        # Common Responses API shape:
        # output -> content -> text
        texts: list[str] = []

        for item in response_dict.get("output", []) or []:
            for content in item.get("content", []) or []:
                if isinstance(content, dict):
                    text_value = content.get("text")
                    if isinstance(text_value, str) and text_value.strip():
                        texts.append(text_value.strip())

        if texts:
            return "\n".join(texts).strip()

        # Some SDKs expose direct text fields.
        for key in ("text", "content", "message"):
            value = response_dict.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    # Fallback string conversion.
    text = str(response)
    if text and text.strip():
        return text.strip()

    return ""


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extract and parse the first JSON object from the model response.
    Fail fast if no valid JSON is present.
    """
    if not text or not text.strip():
        raise ValueError("Empty response from Kestrel workflow.")

    cleaned = text.strip()

    # Remove accidental markdown fences if the model ever returns them.
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Defensive extraction if extra text appears before/after JSON.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Kestrel response did not contain a JSON object.")

    candidate = cleaned[start : end + 1]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Kestrel returned invalid JSON: {exc}") from exc


def validate_prova_payload(data: dict[str, Any]) -> AuditResponse:
    """
    Validate the exact response shape expected by the current Prova frontend.
    Also normalises small optional gaps without inventing scores.
    """

    required_top_level = [
        "overall_score",
        "verdict",
        "headline",
        "summary",
        "exec_summary",
        "gate_level",
        "gate_note",
        "non_negotiable_fails",
        "pillars",
    ]

    missing = [key for key in required_top_level if key not in data]
    if missing:
        raise ValueError(f"Kestrel JSON missing required fields: {missing}")

    if "raw_text" not in data:
        data["raw_text"] = ""

    if not isinstance(data.get("pillars"), list) or len(data["pillars"]) == 0:
        raise ValueError("Kestrel JSON must include a non-empty pillars array.")

    # Ensure fields that the frontend may display are always present.
    for pillar in data["pillars"]:
        pillar.setdefault("au_ref", "")
        pillar.setdefault("nist", "")
        pillar.setdefault("findings", [])
        pillar.setdefault("recommendation", "")

    return AuditResponse(**data)


def run_foundry_workflow(prompt: str) -> str:
    """
    Calls the published Kestrel workflow through Azure AI Foundry.
    """

    logger.info(
        "Calling Foundry workflow name=%s version=%s endpoint=%s",
        KESTREL_WORKFLOW_NAME,
        KESTREL_WORKFLOW_VERSION,
        AZURE_AI_PROJECT_ENDPOINT,
    )

    credential = DefaultAzureCredential()

    project_client = AIProjectClient(
        endpoint=AZURE_AI_PROJECT_ENDPOINT,
        credential=credential,
    )

    with project_client:
        openai_client = project_client.get_openai_client()

        conversation = openai_client.conversations.create()

        response = openai_client.responses.create(
            conversation=conversation.id,
            input=prompt,
            extra_body={
                "agent_reference": {
                    "name": KESTREL_WORKFLOW_NAME,
                    "version": KESTREL_WORKFLOW_VERSION,
                }
            },
        )

    return extract_text_from_foundry_response(response)


# ── Main audit endpoint ──────────────────────────────────────────────────────
@app.post("/audit", response_model=AuditResponse)
async def run_audit(req: AuditRequest) -> AuditResponse:
    if not req.agent_content or len(req.agent_content.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="agent_content too short — paste a full AI use case, system prompt, or agent description.",
        )

    logger.info(
        "Starting Kestrel audit. agent_type=%s deploy_context=%s pillars=%s",
        req.agent_type,
        req.deploy_context,
        req.pillars,
    )

    prompt = build_kestrel_prompt(req)

    try:
        raw_response = run_foundry_workflow(prompt)
        logger.info("Received response from Kestrel workflow. Length=%s", len(raw_response))

        data = extract_json_object(raw_response)
        validated = validate_prova_payload(data)

        logger.info(
            "Kestrel audit completed. score=%s verdict=%s gate=%s",
            validated.overall_score,
            validated.verdict,
            validated.gate_level,
        )

        return validated

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Kestrel audit failed.")
        raise HTTPException(
            status_code=502,
            detail=f"Kestrel workflow failed or returned invalid Prova JSON: {str(exc)}",
        ) from exc
