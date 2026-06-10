<div align="center">

<img src="Mylogo.png" alt="AG Logo" width="88" style="border-radius:50%">

# Prova · AI Governance Inspector

**Powered by the Kestrel Multi-Agent Engine on Azure AI Foundry**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20Prova-c6a243?style=flat-square&logo=github)](https://anir-a.github.io/prova/)
[![API](https://img.shields.io/badge/Backend%20API-kestrel--prova--api-0078d4?style=flat-square&logo=microsoft-azure)](https://github.com/Anir-a/kestrel-prova-api)
[![Hackathon](https://img.shields.io/badge/Agents%20League%202026-Reasoning%20Agents-c6a243?style=flat-square)](https://aka.ms/AgentsLeague/AISF)

*Built for the Microsoft Agents League Hackathon 2026 · Reasoning Agents track*

</div>

---

## The names

**Kestrel** is an Australian bird of prey — small, fast, and extraordinarily precise. A kestrel can hover perfectly still while scanning the ground below, spotting things invisible to others. That is exactly what this engine does: it holds steady over an AI system and finds the risks hiding inside it.

**Prova** means *prove* in Italian. In Bengali, *প্রভা* (prova) means *to shed light*. Both felt right for a tool whose job is to illuminate what is actually inside an AI agent before anyone trusts it.

---

## What it does

Companies are deploying AI agents everywhere. Most of those agents have never been properly checked against the frameworks that govern them — Australia's 8 Ethics Principles, international safety standards, agentic AI security guidance. The checks either happen too late, or not at all.

Prova fixes that. You paste a description of your AI agent. Within 30 seconds, six specialist AI agents inspect it from every angle and return a plain-English report: what passed, what failed, what gate it sits at, and exactly what to fix.

---

## How it works

```
You paste your agent description
           │
           ▼
    FastAPI backend (Azure App Service)
           │  authenticated via Managed Identity — no passwords anywhere
           ▼
    Kestrel Orchestration Engine (Azure AI Foundry)
           │
           ├── Ethics Agent      checks against Australia's 8 AI Ethics Principles
           ├── Risk Agent         maps to NIST AI Risk Management Framework
           ├── Security Agent    scans for OWASP LLM Top 10 vulnerabilities
           ├── Architect Agent   tests architecture against AIP design standards
           ├── Exec Agent         writes the plain-English verdict
           └── Orchestrator      assembles everything into one clean JSON report
           │
           ▼
    Your governance report — score, gate, findings, fixes
```

Each agent reasons independently over its domain. The orchestrator collects their findings and makes the final call. This is not one AI asked to do everything — it is six specialists coordinating, exactly like a real compliance team would.

---

## The Autonomy Gate

Every audit ends with a gate assignment. Think of it as a clearance level — not every AI system has earned the right to act without supervision.

| Gate | Score | What it means |
|---|---|---|
| **G1 — Clear** | 85 – 100 | Governance checks passed. Safe to deploy within assigned infrastructure boundaries. |
| **G2 — Conditional** | 70 – 84 | Significant risks present. Every single output must be reviewed and signed off by a human before the system acts. Not optional. |
| **G4 — Blocked** | 0 – 69 | Critical governance failures detected. This agent cannot go to production. Fix the issues flagged in the report first. |
---

## Try it

**Live:** [anir-a.github.io/prova](https://anir-a.github.io/prova/)

**Paste this to see a G2 result:**
> *"This agent reads job applications from our HR system, scores candidates 1–100 against the role requirements, and presents a shortlist to recruiters. Recruiters manually review and sign off every shortlist before any candidate is contacted. All activity is logged to Azure Monitor."*

**Paste this to see a G4 block:**
> *"Fully autonomous agent that reads loan applications, scores them using historical customer data, approves or rejects automatically, and processes disbursements overnight with no human review at any stage."*

---

## What frameworks it covers

- Australia's 8 AI Ethics Principles (Department of Industry, Science and Resources)
- AI6 Essential Practices — October 2025 update
- ACSC Agentic AI Security Guidance — May 2026 update
- NIST AI Risk Management Framework (Govern · Map · Measure · Manage)
- OWASP LLM Top 10
- AIP-01 to AIP-12 architectural design standards
- APP 1.7 Automated Decision-Making obligations
- MCP Agentic AI Framework

---

## Repositories

| Repo | What's in it |
|---|---|
| [Anir-a/prova](https://github.com/Anir-a/prova) | Frontend — the GitHub Pages web interface |
| [Anir-a/kestrel-prova-api](https://github.com/Anir-a/kestrel-prova-api) | Backend — FastAPI service deployed on Azure App Service |

---

## Running it locally

You will need Python 3.11+, an Azure AI Foundry project, and the Kestrel agent deployed.

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

## A note on how this was built

I am not a professional developer. I am someone who knows AI governance deeply — I built the [Australia AI Guidance Navigator](https://anir-a.github.io/Australia-AI-Guidance-Navigator/) to make Australian AI frameworks accessible to everyone.

For this project, AI assistants helped me write and debug the code. The domain knowledge — which frameworks matter, how they interact, what a governance failure actually looks like — came from years of studying this space, distilled into the Guidance Navigator. Prova is essentially that knowledge made into an automated tool: the Navigator explains the frameworks, Prova checks your AI against them.

The prompts that guide each Kestrel agent were written by me, drawing directly on the content of the Navigator. AI tools helped translate that knowledge into working software.

---

## Governance frameworks applied

The knowledge base behind Prova comes from the [Australia AI Guidance Navigator](https://anir-a.github.io/Australia-AI-Guidance-Navigator/) — an independently maintained reference site covering Australian AI governance in depth. That research is what the Kestrel agents reason against.

---

<div align="center">

Built by **Anirban Ghosal**

[Australia AI Guidance Navigator](https://anir-a.github.io/Australia-AI-Guidance-Navigator/) · [Live Demo](https://anir-a.github.io/prova/)

*Agents League Hackathon 2026 · Reasoning Agents · Microsoft Foundry*

</div>
