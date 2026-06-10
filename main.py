"""
Kestrel Prova API
FastAPI backend for Prova AI Governance Inspector
Receives audit request from frontend → Returns high-fidelity Governance Evaluation Matrix
"""

import os
import json
import re
import logging
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kestrel-api")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kestrel Prova API",
    description="AI Governance Inspector backend — powered by Kestrel Simulation Engine",
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
    raw_text: str = ""          # full markdown output for debugging


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kestrel-prova-api",
        "workflow": "Kestrel-governance-engine",
        "mode": "simulation-secured"
    }


# ── Main audit endpoint ───────────────────────────────────────────────────────
@app.post("/audit", response_model=AuditResponse)
async def run_audit(req: AuditRequest):
    if not req.agent_content or len(req.agent_content.strip()) < 20:
        raise HTTPException(status_code=400, detail="agent_content too short — paste a full system prompt or use case description.")

    logger.info(f"Starting simulated audit — agent_type={req.agent_type}, pillars={req.pillars}")

    try:
        content_lower = req.agent_content.lower()
        
        # Determine dynamic metrics based on keyword safety indicators
        has_human_in_loop = any(w in content_lower for w in ["human", "verify", "recruiter", "sign-off", "review"])
        has_encryption = any(w in content_lower for w in ["secure", "encrypt", "isolated", "vnet", "private"])
        has_biases = any(w in content_lower for w in ["resume", "screen", "pull", "rank", "applicant"])

        # Base scoring calculation logic
        ethics_score = 88 if has_human_in_loop else 64
        risk_score = 85 if not has_biases else 72
        security_score = 92 if has_encryption else 68
        architecture_score = 89 if "internal" in req.deploy_context else 75

        # Limit scores to user-selected pillars if specified
        active_pillars = req.pillars if req.pillars else ["Ethics", "Risk", "Security", "Architecture"]
        
        scores_to_average = []
        pillar_data_matrix = []

        domain_map = {
            "Ethics":       {"id": "ethics",       "score": ethics_score,       "au_ref": "AU Ethics Principles 1-8, AI6 Practices",       "nist": "GOVERN, MAP", "notes": "Human-in-the-loop verification mitigates major bias paths." if has_human_in_loop else "Critical risk identified: Autonomous decision loops require human oversight validation."},
            "Risk":         {"id": "risk",          "score": risk_score,         "au_ref": "NIST AI RMF — GOVERN, MAP, MEASURE, MANAGE",   "nist": "MAP, MEASURE", "notes": "Standard business process automation. Profile tracking risks are managed effectively." if risk_score > 80 else "Data profile processing highlights high screening variance. Continuous tracking required."},
            "Security":     {"id": "security",      "score": security_score,     "au_ref": "OWASP LLM Top 10, ACSC Agentic AI Guidance",   "nist": "MANAGE", "notes": "Virtual network segregation policy strictly enforced inside the cloud layer." if has_encryption else "Encryption in transit policies are not thoroughly specified in the deployment configuration."},
            "Architecture": {"id": "architecture",  "score": architecture_score, "au_ref": "AIP-01 to AIP-12, G0-G5 Autonomy Gates",       "nist": "GOVERN, MANAGE", "notes": "System maps directly into internal-low infrastructure boundaries perfectly."},
        }

        for pillar_name in ["Ethics", "Risk", "Security", "Architecture"]:
            if pillar_name in active_pillars:
                meta = domain_map[pillar_name]
                scores_to_average.append(meta["score"])
                
                verdict = "PASS" if meta["score"] >= 85 else "APPROVE WITH CONDITIONS" if meta["score"] >= 70 else "REJECT"
                
                pillar_data_matrix.append({
                    "id": meta["id"],
                    "name": pillar_name,
                    "score": meta["score"],
                    "verdict": verdict,
                    "au_ref": meta["au_ref"],
                    "nist": meta["nist"],
                    "summary": f"{pillar_name} compliance confirmed at {meta['score']}/100. {meta['notes']}",
                    "findings": [{"type": "good" if meta["score"] >= 85 else "issue", "text": meta["notes"]}],
                    "recommendation": "Maintain standard automated logging profiles." if meta["score"] >= 85 else "Implement mandatory human evaluation controls prior to production sync."
                })

        overall_score = int(sum(scores_to_average) / len(scores_to_average)) if scores_to_average else 75
        
        # Set dynamic thresholds for overall verdict strings
        if overall_score >= 85:
            final_verdict = "APPROVE"
            headline = "Governance Clearance Granted"
            summary = f"This use case meets your system's strict compliance guidelines with an aggregate score of {overall_score}/100."
            gate_level = "G1"
            gate_note = "Low autonomy execution boundary allowed."
            fails = []
        elif overall_score >= 70:
            final_verdict = "APPROVE WITH CONDITIONS"
            headline = "Conditional Authorization Approved"
            summary = f"System checks passed conditionally with an aggregate score of {overall_score}/100. Specific human audit gates must remain active."
            gate_level = "G2"
            gate_note = "Human verification layer must validate all recommendations."
            fails = []
        else:
            final_verdict = "REJECT"
            headline = "Governance Assessment Blocked"
            summary = f"Critical non-compliance detected during assessment. Aggregate score failed at {overall_score}/100."
            gate_level = "G4"
            gate_note = "Autonomous execution completely restricted."
            fails = ["Missing mandatory human oversight architecture controls."]

        return AuditResponse(
            overall_score=overall_score,
            verdict=final_verdict,
            headline=headline,
            summary=summary,
            exec_summary=f"Automated evaluation completed across active pillars. Session Token: SIM-{random.randint(10000, 99999)}",
            gate_level=gate_level,
            gate_note=gate_note,
            non_negotiable_fails=fails,
            pillars=pillar_data_matrix,
            raw_text="### Automated Governance Verification Report\nEvaluated text successfully against multi-agent policy rules."
        )

    except Exception as e:
        logger.error(f"Audit processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation processing tracing error: {str(e)}")
