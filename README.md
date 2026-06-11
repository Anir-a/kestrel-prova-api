<div align="center">

<img src="https://raw.githubusercontent.com/Anir-a/prova/main/Mylogo.png" alt="AG Logo" width="88" style="border-radius:50%">

# Prova · AI Governance Inspector

**Powered by the Kestrel Multi-Agent Engine on Azure AI Foundry**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20Prova-c6a243?style=flat-square&logo=github)](https://anir-a.github.io/prova/)
[![Backend API](https://img.shields.io/badge/Backend%20API-kestrel--prova--api-0078d4?style=flat-square&logo=microsoft-azure)](https://github.com/Anir-a/kestrel-prova-api)
[![Hackathon](https://img.shields.io/badge/Agents%20League%202026-Reasoning%20Agents-c6a243?style=flat-square)](https://aka.ms/AgentsLeague/AISF)

*Built for the Microsoft Agents League Hackathon 2026 · Reasoning Agents track*

</div>

---

## The names

**Kestrel** is an Australian bird of prey — small, fast, and extraordinarily precise. A kestrel can hover perfectly still in mid-air while scanning the ground below, spotting things invisible to everyone else. That is exactly what this engine does: it holds steady over an AI system and finds the risks hiding inside it.

**Prova** means *prove* in Italian. In Bengali, *প্রভা* (prova) means *to shed light*. Both felt right for a tool whose only job is to illuminate what is actually inside an AI agent before anyone trusts it with real decisions.

---

## The problem

Companies are deploying AI agents everywhere. Most of those agents have never been properly checked against the frameworks that govern them — Australia's 8 Ethics Principles, international safety standards, agentic AI security guidance. Compliance reviews either happen too late, or not at all.

The result is AI making decisions about people — hiring, lending, healthcare, benefits — with nobody verifying whether the system is actually safe, fair, or legally sound.

Prova fixes that.

---

## What it does

Paste a description of your AI agent. Within 30 seconds, six specialist AI agents inspect it from every angle and return a plain-English report: what passed, what failed, which of the 5 auto-fail conditions were triggered, what gate it sits at (G0–G5), and exactly what to fix before it ships.

**At a glance:**

| | |
|---|---|
| 🔍 **9 governance pillars** | Every audit covers all nine pillars simultaneously |
| ⛔ **5 auto-fail conditions** | Triggered regardless of overall score — instant block |
| 🚦 **Gates G0 – G5** | Six-level autonomy classification — from exempt to prohibited |
| ⏱ **Under 70 seconds** | Full multi-agent pipeline, structured JSON report |
| 🔒 **Zero hardcoded secrets** | Azure Managed Identity — no passwords anywhere in the code |

---

## How it works

```
You paste your agent description
           │
           ▼
    FastAPI backend  (Azure App Service · Australia East)
           │  authenticated via Azure Managed Identity
           ▼
    Kestrel Orchestration Engine  (Azure AI Foundry · GPT-4.1-mini)
           │
           ├── Ethics Agent      AU 8 Ethics Principles · AI6 Essential Practices
           ├── Risk Agent         NIST AI RMF · Govern · Map · Measure · Manage
           ├── Security Agent    OWASP LLM Top 10 · ACSC Agentic AI Guidance (May 2026)
           ├── Architect Agent   AIP-01–12 · Autonomy Gate assignment G0–G5
           ├── Exec Agent         Plain-English verdict · remediation guidance
           └── Kestrel Orchestrator   Synthesises all findings → structured JSON report
           │
           ▼
    Score · Gate · 9 pillar breakdowns · auto-fail flags · fixes
```

Each agent reasons independently over its own governance domain. The orchestrator collects their findings and makes the final call. This is not one AI asked to do everything — it is six specialists coordinating, the same way a real compliance team would.

---
## Demo Video

Watch the Prova / Kestrel demo here:

[Final Presentation – Prova AI Governance Inspector](https://youtu.be/FP_Cljb7eWE)

---

## The 9 governance pillars

Every audit assesses all nine pillars. Each maps to one or more of the frameworks below.

| Pillar | Frameworks |
|---|---|
| **Wellbeing** | AU Ethics P1 |
| **Human-Centred** | AU Ethics P2 · AIP-04 |
| **Fairness** | AU Ethics P3 |
| **Privacy & Security** | AU Ethics P4 · AIP-05 |
| **Reliability** | AU Ethics P5 · AI6 P5 |
| **Transparency** | AU Ethics P6 · AIP-07 |
| **Contestability** | AU Ethics P7 · AI6 P6 |
| **Accountability** | AU Ethics P8 · AI6 P1 |
| **Agentic Controls** | ACSC May 2026 · G0–G5 |

### Auto-fail conditions

Five conditions trigger an immediate G4 or G5 block regardless of the overall score:

1. Fully autonomous financial or legal decisions with no human review
2. Biometric or demographic data used in automated ranking or scoring
3. No human-in-the-loop mechanism in a regulated industry context
4. Prompt injection vulnerability with access to sensitive data or actions
5. Agentic system with unbounded execution scope and no kill switch

---

## The Autonomy Gate

Every audit ends with a gate assignment. Think of it as a clearance level — not every AI system has earned the right to act without supervision.

| Gate | Score | What it means |
|---|---|---|
| **G0 — Exempt** | — | Minimal AI involvement. No governance review required. |
| **G1 — Clear** | 85 – 100 | Governance checks passed. Safe to deploy within assigned infrastructure boundaries. |
| **G2 — Conditional** | 70 – 84 | Significant risks present. Every output must be reviewed and signed off by a human before the system acts. Not optional. |
| **G3 — Restricted** | 50 – 69 | Material failures across multiple pillars. Limited internal deployment only — no customer-facing or automated decision use. |
| **G4 — Blocked** | 30 – 49 | Critical governance failures. Cannot go to production until all flagged issues are resolved. |
| **G5 — Prohibited** | 0 – 29 | Fundamental violations detected. Deployment prohibited. Complete redesign required before re-submission. |

---

## Try it

**Live:** [anir-a.github.io/prova](https://anir-a.github.io/prova/)

Use these four scenarios to see the full gate range in action.

---

**G1 — Clear** ✅

> *"Internal read-only knowledge assistant for our legal team. It searches approved policy documents and returns relevant excerpts with source citations. It cannot send emails, take actions, or access any external systems. All queries are logged. A lawyer reviews any response before it is used in a matter."*

No autonomous actions, no sensitive decisions, full logging, human review in place. Expect a clean pass above 85.

---

**G2 — Conditional** ⚠️

> *"This agent reads job applications from our HR system, scores candidates 1–100 against the role requirements, and presents a shortlist to recruiters. Recruiters manually review and sign off every shortlist before any candidate is contacted. All activity is logged to Azure Monitor."*

Human oversight is present but the scoring of people introduces fairness and bias risk. Expect 70–84 with mandatory human sign-off required.

---

**G3 — Restricted** 🔶

> *"This agent monitors customer support tickets and automatically categorises them by urgency, assigns them to the right team, and sends an acknowledgement email to the customer. It does not resolve tickets — only routes them. There is no logging of what categories are assigned or why."*

No direct harm, but no logging and no explainability of routing decisions means it fails transparency and accountability. Expect 50–69 — internal use only, not customer-facing.

---

**G4 — Blocked** ❌

> *"Fully autonomous agent that reads incoming loan applications, scores them using historical customer demographic data, approves or rejects automatically, and processes disbursements overnight with no human review at any stage."*

Automated financial decisions on people, demographic data in scoring, zero human oversight. Expect a hard block below 49 with auto-fail conditions triggered.

---

## Framework coverage

| Framework | What it covers |
|---|---|
| **AU 8 AI Ethics Principles** (DISR) | Human wellbeing, fairness, privacy, reliability, transparency, contestability, accountability |
| **AI6 Essential Practices** (Oct 2025) | Accountability structures, business process impact, response testing |
| **ACSC Agentic AI Guidance** (May 2026) | Multi-agent coordination risks, execution limits, cascading token threats |
| **NIST AI RMF** | Govern · Map · Measure · Manage |
| **OWASP LLM Top 10** | Prompt injection, excessive agency, insecure credential storage, lateral data exposure |
| **AIP-01 to AIP-12** | Architectural isolation boundaries and design standards |
| **APP 1.7 Automated Decisions** (Dec 2026) | Obligations for AI in automated decision-making |
| **MCP Agentic AI Framework** | Multi-agent protocol governance |

---

## Repositories

| Repo | What's in it |
|---|---|
| [Anir-a/prova](https://github.com/Anir-a/prova) | Frontend — the GitHub Pages web interface |
| [Anir-a/kestrel-prova-api](https://github.com/Anir-a/kestrel-prova-api) | Backend — FastAPI service on Azure App Service |

---

## Running it locally

You will need Python 3.11+, an Azure AI Foundry project, and the Kestrel agent already deployed.

```bash
git clone https://github.com/Anir-a/kestrel-prova-api.git
cd kestrel-prova-api

export AZURE_AI_PROJECT_ENDPOINT="https://your-foundry-endpoint.azure.com"
export KESTREL_AGENT_ID="your-agent-guid"
export ALLOWED_ORIGINS="https://anir-a.github.io"

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open `index.html` from the [prova](https://github.com/Anir-a/prova) repo in your browser.

---

## How this was built

I am not a professional developer. I am someone who knows AI governance deeply — I built the [Australia AI Guidance Navigator](https://anir-a.github.io/Australia-AI-Guidance-Navigator/) to make Australian AI frameworks accessible to everyone, and spent months studying these frameworks before writing a single line of this project.

For Prova, AI assistants helped me write and debug the code, and helped optimise the prompts that guide each Kestrel agent. The domain knowledge — which frameworks matter, how they interact, what an actual governance failure looks like in a system prompt — came from that research, distilled into the Guidance Navigator. Prova is essentially that knowledge made into an automated tool: the Navigator explains the frameworks, Prova checks your AI against them.

The six Kestrel agent prompts were written by me, drawing directly on the content of the Navigator. AI tools helped translate that knowledge into working software.

## Engineering Challenges & Lessons Learned

Building Kestrel and Prova involved significantly more than prompt engineering. Challenges included Azure AI Foundry model availability, quota constraints, governance knowledge base design, multi-agent orchestration, Azure App Service deployment, workflow integration, and schema validation.

See [Lessons_Learned.md](docs/Lessons_Learned.md) for the complete project journey and lessons learned.
---

<div align="center">

Built by **Anirban Ghosal**

[Australia AI Guidance Navigator](https://anir-a.github.io/Australia-AI-Guidance-Navigator/) · [Live Demo](https://anir-a.github.io/prova/)

*Agents League Hackathon 2026 · Reasoning Agents · Microsoft Foundry*

</div>
