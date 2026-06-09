"""
Kestrel Prova API
FastAPI backend for Prova AI Governance Inspector
Frontend → FastAPI → Kestrel Governance Workflow on Azure AI Foundry → JSON response
"""

import os
import re
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ResponseStreamEventType
from azure.identity import DefaultAzureCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kestrel-api")

app = FastAPI(
    title="Kestrel Prova API",
    description="AI Governance Inspector backend — powered by Kestrel on Azure AI Foundry",
    version="1.1.0"
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://anir-a.github.io").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
WORKFLOW_NAME = os.getenv("KESTREL_WORKFLOW_NAME", "Kestrel-governance-engine")


class AuditRequest(BaseModel):
    agent_content: str
    agent_type: str = "general"
    deploy_context: str = "internal-low"
    pillars: list[str] = []


class AuditResponse(BaseModel):
    overall_score: int
    verdict: str
    headline: str
    summary: str
    exec_summary: str
    gate_level: str
    gate_note: str
    non_negotiable_fails: list[str]
    pillars: list[dict]
    raw_text: str = ""


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kestrel-prova-api",
        "foundry_endpoint": PROJECT_ENDPOINT or "NOT SET",
        "workflow": WORKFLOW_NAME
    }


def build_kestrel_prompt(req: AuditRequest) -> str:
    content = req.agent_content.strip()
    if len(content) > 3000:
        content = content[:3000] + "\n...[truncated for assessment]"

    pillars_str = ", ".join(req.pillars) if req.pillars else "all governance pillars"

    return f"""Assess this AI use case for governance compliance.

Agent type: {req.agent_type}
Deployment context: {req.deploy_context}
Governance pillars to assess: {pillars_str}

AGENT CONTENT:
{content}

Provide the full governance assessment including:
- Governance Decision table
- Domain scores
- Governance Score
- Verdict
- Autonomy Gate
- Auto-fail checks
- Board Recommendation
- Required actions."""


def parse_kestrel_output(text: str) -> dict:
    result = {
        "overall_score": 0,
        "verdict": "REJECT",
        "headline": "Governance assessment complete",
        "summary": "",
        "exec_summary": "",
        "gate_level": "G1",
        "gate_note": "Autonomy gate assigned by Kestrel",
        "non_negotiable_fails": [],
        "pillars": [],
        "raw_text": text
    }

    score_match = re.search(r'Governance Score[:\s]+(\d+)', text, re.IGNORECASE)
    if score_match:
        result["overall_score"] = int(score_match.group(1))

    verdict_match = re.search(r'Verdict[:\s]+(APPROVE WITH CONDITIONS|APPROVE|REJECT|PASS|FAIL)', text, re.IGNORECASE)
    if verdict_match:
        v = verdict_match.group(1).upper()
        if "CONDITIONS" in v:
            result["verdict"] = "APPROVE WITH CONDITIONS"
        elif v in ["APPROVE", "PASS"]:
            result["verdict"] = "APPROVE"
        else:
            result["verdict"] = "REJECT"

    gate_match = re.search(r'Autonomy Gate[:\s]+(G\d)[^\n]*[-—]?\s*([^\n]+)?', text, re.IGNORECASE)
    if gate_match:
        result["gate_level"] = gate_match.group(1).upper()
        if gate_match.group(2):
            result["gate_note"] = gate_match.group(2).strip()

    board_match = re.search(r'Board Recommendation[:\s]+([^\n]+)', text, re.IGNORECASE)
    if board_match:
        result["headline"] = board_match.group(1).strip()
        result["exec_summary"] = board_match.group(1).strip()
    else:
        result["exec_summary"] = text[:800]

    domain_map = {
        "Ethics": {"id": "ethics", "au_ref": "AU Ethics Principles, AI6 Practices", "nist": "GOVERN, MAP"},
        "Risk": {"id": "risk", "au_ref": "NIST AI RMF", "nist": "MAP, MEASURE"},
        "Security": {"id": "security", "au_ref": "OWASP LLM Top 10, ACSC Agentic AI Guidance", "nist": "MANAGE"},
        "Architecture": {"id": "architecture", "au_ref": "AIP-01 to AIP-12, G0-G5 Autonomy Gates", "nist": "GOVERN, MANAGE"},
    }

    table_match = re.search(r'\|.*Domain.*\|.*Score.*\|.*Status.*\|(.*?)(?=\*\*Governance Score|\Z)', text, re.DOTALL | re.IGNORECASE)

    if table_match:
        table_text = table_match.group(1)
        for domain, meta in domain_map.items():
            row = re.search(rf'\|\s*{domain}\s*\|\s*(\d+)/100\s*\|\s*([^\|]+)\|', table_text, re.IGNORECASE)
            if row:
                score = int(row.group(1))
                status_raw = row.group(2).strip()

                if "green" in status_raw.lower() or "pass" in status_raw.lower() or "🟢" in status_raw:
                    verdict = "PASS"
                elif "amber" in status_raw.lower() or "conditional" in status_raw.lower() or "🟡" in status_raw:
                    verdict = "APPROVE WITH CONDITIONS"
                else:
                    verdict = "REJECT"

                result["pillars"].append({
                    "id": meta["id"],
                    "name": domain,
                    "score": score,
                    "verdict": verdict,
                    "au_ref": meta["au_ref"],
                    "nist": meta["nist"],
                    "summary": f"{domain} assessment — score {score}/100",
                    "findings": [{"type": "issue", "text": f"See full {domain} assessment in Kestrel output."}],
                    "recommendation": f"Review {domain} findings and implement required actions before production."
                })

    if not result["pillars"]:
        for domain, meta in domain_map.items():
            result["pillars"].append({
                "id": meta["id"],
                "name": domain,
                "score": 0,
                "verdict": "REJECT",
                "au_ref": meta["au_ref"],
                "nist": meta["nist"],
                "summary": f"{domain} assessment returned by Kestrel. See raw output.",
                "findings": [{"type": "issue", "text": "See raw Kestrel output."}],
                "recommendation": "Review Kestrel assessment and complete remediation."
            })

    score = result["overall_score"]
    if score >= 85:
        result["summary"] = f"This AI use case meets the required governance threshold with a score of {score}/100."
    elif score >= 70:
        result["summary"] = f"This AI use case conditionally meets governance requirements with a score of {score}/100."
    else:
        result["summary"] = f"This AI use case does not meet governance requirements. Score {score}/100."

    return result


@app.post("/audit", response_model=AuditResponse)
async def run_audit(req: AuditRequest):

    if not PROJECT_ENDPOINT:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: AZURE_AI_PROJECT_ENDPOINT is not set."
        )

    if not req.agent_content or len(req.agent_content.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="agent_content too short — paste a full system prompt or use case description."
        )

    try:
        credential = DefaultAzureCredential()
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )

        user_message = build_kestrel_prompt(req)
        logger.info(f"Starting audit via workflow={WORKFLOW_NAME}")

        openai_client = client.get_openai_client()
        conversation = openai_client.conversations.create()

        stream = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {
                    "name": WORKFLOW_NAME,
                    "type": "agent_reference"
                }
            },
            input=user_message,
            stream=True,
            metadata={"x-ms-debug-mode-enabled": "1"},
        )

        raw_text = ""

        for event in stream:
            if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA:
                raw_text += event.delta
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
                raw_text += event.text

        openai_client.conversations.delete(conversation_id=conversation.id)

        if not raw_text.strip():
            raise HTTPException(status_code=502, detail="Kestrel returned no assessment.")

        logger.info(f"Kestrel response received — {len(raw_text)} chars")

        result = parse_kestrel_output(raw_text)
        return AuditResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audit error: {str(e)}")
