"""
Kestrel Prova API
FastAPI backend for Prova AI Governance Inspector
Receives audit request from frontend → calls Kestrel agent on Azure AI Foundry → returns JSON
"""

import os
import json
import re
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kestrel-api")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kestrel Prova API",
    description="AI Governance Inspector backend — powered by Kestrel on Azure AI Foundry",
    version="1.0.0"
)

# ── CORS — allow only the Prova GitHub Pages frontend ────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://anir-a.github.io").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

# ── Azure AI Foundry config — from App Service Environment Variables ──────────
PROJECT_ENDPOINT   = os.getenv("AZURE_AI_PROJECT_ENDPOINT")   # your project endpoint
AGENT_ID           = os.getenv("KESTREL_AGENT_ID")            # kestrel-orchestrator agent ID


# ── Request / Response models ─────────────────────────────────────────────────
class AuditRequest(BaseModel):
    agent_content: str          # system prompt or use case description
    agent_type: str = "general"
    deploy_context: str = "internal-low"
    pillars: list[str] = []     # selected governance pillars


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
    raw_text: str = ""          # full Kestrel markdown output for debugging


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kestrel-prova-api",
        "foundry_endpoint": PROJECT_ENDPOINT or "NOT SET",
        "workflow": "Kestrel-governance-engine"
    }


# ── Build the prompt sent to Kestrel ─────────────────────────────────────────
def build_kestrel_prompt(req: AuditRequest) -> str:
    content = req.agent_content
    if len(content) > 3000:
        content = content[:3000] + "\n...[truncated for assessment]"

    pillars_str = ", ".join(req.pillars) if req.pillars else "all governance pillars"

    return f"""Assess this AI use case for governance compliance.

Agent type: {req.agent_type}
Deployment context: {req.deploy_context}
Governance pillars to assess: {pillars_str}

AGENT CONTENT:
{content}

Provide the full governance assessment including the Governance Decision table, scores, verdict, and Board Recommendation."""


# ── Parse Kestrel markdown output into structured JSON ────────────────────────
def parse_kestrel_output(text: str) -> dict:
    """
    Parse Kestrel's markdown governance report into structured JSON
    for the Prova frontend renderer.
    """

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

    # ── Overall score ──
    score_match = re.search(r'Governance Score[:\s]+(\d+)', text, re.IGNORECASE)
    if not score_match:
        score_match = re.search(r'Overall(?:\s+Average|\s+Score)?\s*\|\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    if not score_match:
        score_match = re.search(r'Overall(?:\s+Average|\s+Score)?[:\s]+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    if score_match:
        result["overall_score"] = int(round(float(score_match.group(1))))

    # ── Verdict ──
    verdict_match = re.search(r'(?:Final Governance Decision|Overall Governance Verdict|Verdict)[:\s#*]+(APPROVE WITH CONTROLS|ACCEPT WITH CONTROLS|APPROVE WITH CONDITIONS|APPROVE|ACCEPT|REJECT|PASS|FAIL)', text, re.IGNORECASE)
    if verdict_match:
        v = verdict_match.group(1).upper()
        if "CONTROLS" in v or "CONDITIONS" in v:
            result["verdict"] = "APPROVE WITH CONDITIONS"
        elif v in ["APPROVE", "ACCEPT", "PASS"]:
            result["verdict"] = "APPROVE"
        else:
            result["verdict"] = "REJECT"

    # ── Gate ──
    gate_match = re.search(r'Autonomy Gate[:\s]+G(\d)[^\n]*[-—]?\s*([^\n]+)?', text, re.IGNORECASE)
    if gate_match:
        result["gate_level"] = f"G{gate_match.group(1)}"
        if gate_match.group(2):
            result["gate_note"] = gate_match.group(2).strip()

    # ── Board Recommendation (use as headline) ──
    board_match = re.search(r'Board Recommendation[:\s]+([^\n]+)', text, re.IGNORECASE)
    if board_match:
        result["headline"] = board_match.group(1).strip()
        result["exec_summary"] = board_match.group(1).strip()

    # ── Non-negotiable fails ──
    nn_section = re.search(r'Auto-Fail Check(.*?)(?=\*\*Ethics|\*\*Risk|\*\*Security|\*\*Architecture|##)', text, re.DOTALL | re.IGNORECASE)
    if nn_section:
        nn_text = nn_section.group(1)
        fails = re.findall(r'[-•*]\s*(.+)', nn_text)
        none_identified = re.search(r'none identified', nn_text, re.IGNORECASE)
        if not none_identified:
            result["non_negotiable_fails"] = [f.strip() for f in fails if f.strip()]

    # ── Domain scores from Kestrel score table ──
    domain_map = {
        "Ethics":       {"id": "ethics",       "au_ref": "AU Ethics Principles 1-8, AI6 Practices",       "nist": "GOVERN, MAP"},
        "Risk":         {"id": "risk",          "au_ref": "NIST AI RMF — GOVERN, MAP, MEASURE, MANAGE",   "nist": "MAP, MEASURE"},
        "Security":     {"id": "security",      "au_ref": "OWASP LLM Top 10, ACSC Agentic AI Guidance",   "nist": "MANAGE"},
        "Architecture": {"id": "architecture",  "au_ref": "AIP-01 to AIP-12, G0-G5 Autonomy Gates",       "nist": "GOVERN, MANAGE"},
    }

    for domain, meta in domain_map.items():
        row = re.search(rf'\|\s*{domain}\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*([^\|]+)\|', text, re.IGNORECASE)
        if row:
            score = int(round(float(row.group(1))))
            notes = row.group(2).strip()
            if score >= 85:
                verdict = "PASS"
            elif score >= 70:
                verdict = "APPROVE WITH CONDITIONS"
            else:
                verdict = "REJECT"

            findings = extract_domain_findings(text, domain)
            rec = extract_domain_recommendation(text, domain)

            result["pillars"].append({
                "id":             meta["id"],
                "name":           domain,
                "score":          score,
                "verdict":        verdict,
                "au_ref":         meta["au_ref"],
                "nist":           meta["nist"],
                "summary":        f"{domain} assessment — score {score}/100. {notes}",
                "findings":       findings,
                "recommendation": rec
            })

    # ── Fallback summary ──
    score = result["overall_score"]
    if score >= 85:
        result["summary"] = f"This AI use case meets the required governance threshold with a score of {score}/100."
    elif score >= 70:
        result["summary"] = f"This AI use case conditionally meets governance requirements with a score of {score}/100. Specific actions required before deployment."
    else:
        result["summary"] = f"This AI use case does not meet governance requirements. Score {score}/100. Immediate remediation required."

    return result


def extract_domain_findings(text: str, domain: str) -> list[dict]:
    """Extract bullet-point findings for a given domain from Kestrel output."""
    pattern = rf'\*\*{domain}\*\*[^\n]*\n(.*?)(?=\*\*Ethics|\*\*Risk|\*\*Security|\*\*Architecture|\*\*Governance|##|\Z)'
    section = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not section:
        return [{"type": "issue", "text": f"See full {domain} assessment in governance report."}]

    section_text = section.group(1)
    bullets = re.findall(r'[-•*]\s*(.+)', section_text)
    findings = []
    for b in bullets[:3]:
        b = b.strip()
        if not b:
            continue
        ftype = "fail" if any(w in b.lower() for w in ["missing", "no ", "absent", "fail", "critical"]) else \
                "issue" if any(w in b.lower() for w in ["risk", "gap", "concern", "unclear", "limited"]) else "good"
        findings.append({"type": ftype, "text": b})

    return findings if findings else [{"type": "issue", "text": f"See full {domain} assessment."}]


def extract_domain_recommendation(text: str, domain: str) -> str:
    """Extract or generate a recommendation for a domain."""
    pattern = rf'{domain}.*?recommend[^\n]*([^\n]+)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return f"Review {domain} findings and implement required controls before deployment."


# ── Main audit endpoint ───────────────────────────────────────────────────────
@app.post("/audit", response_model=AuditResponse)
async def run_audit(req: AuditRequest):

    if not PROJECT_ENDPOINT:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: AZURE_AI_PROJECT_ENDPOINT is not set."
        )

    if not req.agent_content or len(req.agent_content.strip()) < 20:
        raise HTTPException(status_code=400, detail="agent_content too short — paste a full system prompt or use case description.")

    try:
        # ── Connect to Azure AI Foundry using Managed Identity ──
        credential = DefaultAzureCredential()
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )

        # ── Build prompt ──
        user_message = build_kestrel_prompt(req)
        logger.info(f"Starting audit — workflow=Kestrel-governance-engine, agent_type={req.agent_type}, pillars={req.pillars}")

        # ── Call Kestrel governance workflow using standard non-streaming execution ──
        openai_client = client.get_openai_client()
        conversation = openai_client.conversations.create()

        try:
            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent_reference": {
                        "name": "Kestrel-governance-engine",
                        "type": "agent_reference"
                    }
                },
                input=user_message,
                stream=False, # ➔ Disabled streaming to cleanly pass large multi-line real paragraphs
                metadata={"x-ms-debug-mode-enabled": "1"},
            )

            # ── Direct Key Extraction Fallbacks ──
            raw_text = ""
            
            # Primary: Try extracting the standard response model choices content
            if hasattr(response, "choices") and response.choices:
                raw_text = response.choices[0].message.content or ""
            
            # Secondary Fallback: If it returns as a custom property dictionary object
            if not raw_text and isinstance(response, dict):
                raw_text = (
                    response.get("properties", {})
                    .get("outputs", {})
                    .get("Local.FinalGovernanceDecision", "")
                )
            
            # Final Fallback: Attempt string deduction if text field is exposed
            if not raw_text and hasattr(response, "text"):
                raw_text = response.text or ""

        finally:
            try:
                openai_client.conversations.delete(conversation_id=conversation.id)
            except Exception as cleanup_error:
                logger.warning(f"Conversation cleanup failed: {cleanup_error}")

        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=502, detail="Kestrel returned no assessment.")

        logger.info(f"Kestrel response received — {len(raw_text)} chars")

        # ── Parse into structured JSON ──
        result = parse_kestrel_output(raw_text)
        return AuditResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audit error: {str(e)}")
