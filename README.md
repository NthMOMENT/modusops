# MODUS OPS

**Adversarial AI justice engine. Four agents investigate real-world crimes, settle verdicts on-chain.**

[![License: BUSL-1.1](https://img.shields.io/badge/License-BUSL--1.1-blue.svg)](https://spdx.org/licenses/BUSL-1.1.html)
[![Chain: Arbitrum One](https://img.shields.io/badge/Chain-Arbitrum%20One-1B63E8.svg)](https://arbiscan.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-1B63E8.svg)](https://python.org)

---

## What It Does

Modus Ops is a production-grade, multi-agent AI system that investigates crimes through an adversarial panel of four specialized agents. The agents do not summarize evidence. They argue against each other and the final verdict is committed on-chain as a tamper-proof chain-of-custody record.

**The system accepts case documents. It returns a verdict.**

---

## The Four Agents

```
┌─────────────────────────────────────────────────────────────────┐
│                        CASE DOCUMENTS                           │
│              (PDFs, bank statements, reports)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT #1 — LAW ENFORCEMENT (Token #1416)                       │
│  Parses documents. Extracts entities, timelines, anomalies.     │
│  Determines jurisdiction: LOCAL / STATE / FEDERAL.              │
│  Flags all numerical claims for mathematical verification.      │
└───────────┬─────────────────────────────────────────────────────┘
            │  Verified facts
            ├──────────────────────┐
            ▼                      ▼
┌───────────────────┐   ┌──────────────────────────────────────┐
│ AGENT #2 — DA     │   │ AGENT #3 — DEFENSE COUNSEL           │
│ (Token #1417)     │   │ (Token #1418)                        │
│                   │   │                                      │
│ Builds the        │   │ Tears the prosecution case apart.    │
│ strongest case.   │   │ Identifies reasonable doubt,         │
│ Maps facts to     │   │ chain-of-custody breaks, Daubert     │
│ statute. Cannot   │   │ challenges. Cannot concede without   │
│ hedge.            │   │ a formal motion to suppress.         │
└───────┬───────────┘   └───────────────┬──────────────────────┘
        │  Both run in parallel         │
        └──────────────┬────────────────┘
                       │  Adversarial record
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT #4 — PRESIDING JUDGE (Token #1419)                       │
│  Reviews prosecution + defense submissions for logical          │
│  consistency and procedural fairness. Issues a structured       │
│  verdict with a confidence score (0–100).                       │
│                                                                 │
│  VERDICT: PROCEED | DISMISS | ESCALATE | REVIEW                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  ON-CHAIN — ARBITRUM ONE                                        │
│  Verdict hashed (SHA-256) and committed to the verdict          │
│  contract. Indexed by The Graph. Immutable chain-of-custody.    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
- **FastAPI** (Python 3.10+) — REST API, case ingestion, agent orchestration
- **LangGraph** — deterministic adversarial pipeline with parallel fan-out (DA + Defense run simultaneously)
- **Custom LLM** — powers all four agents with role-locked system prompts
- **Unstructured** — PDF and document parsing for case file ingestion

### Web3
- **Arbitrum One** — verdict contract + ERC-8004 agent identity registry (tokens #1416–#1419)
- **The Graph** — subgraph indexing `VerdictLogged` events; frontend queries case history via GraphQL
- **Circle Agent Stack (Arc)** — four agent wallets on Arc; USDC nanopayments per completed investigation step
- **Hedera x402** — HTTP 402 payment rail gating MCP tool calls
- **Bazantic** — x402-gated MCP server monetization

### Frontend
- **Next.js 14** (App Router, CSS Modules, static export)
- Live at [modusops.xyz](https://modusops.xyz)

---

## Agent Identity — ERC-8004 on Arbitrum One

Each agent is a registered on-chain identity, not just a software process.

| Token | Agent | Role |
|-------|-------|------|
| #1416 | Law Enforcement | Investigator & Escalation Engine |
| #1417 | Prosecutor (DA) | Adversarial case builder |
| #1418 | Defense Counsel | Red team & reasonable doubt |
| #1419 | Presiding Judge | Arbitration & verdict |

---

## Verdict Object

Every case produces a structured verdict committed on-chain:

```json
{
  "case_id": "OBE-2026-001",
  "timestamp": 1757116800,
  "verdict": "ESCALATE",
  "confidence_score": 74,
  "jurisdiction": "FEDERAL",
  "prosecution_brief": "...",
  "defense_memorandum": "...",
  "judicial_summary": "...",
  "evidence_hashes": [
    "a3f2c1...",
    "b8e4d2...",
    "c7a9f3..."
  ],
  "agent_tokens": {
    "law_enforcement": 1416,
    "prosecutor": 1417,
    "defense": 1418,
    "judge": 1419
  },
  "on_chain_tx": "0x..."
}
```

---

## Setup

### Requirements
- Python 3.10+
- Node.js 18+
- Foundry (for contract deployment)

### Backend

```bash
git clone https://github.com/NthMOMENT/modusops.git
cd modusops

cp .env.example api/.env
# Fill in your values in api/.env

pip install -r api/requirements.txt

uvicorn api.main:app --host 127.0.0.1 --port 8000
```

### Environment Variables

```
CUSTOM_LLM_API_KEY=        # LLM API key
CUSTOM_LLM_BASE_URL=       # OpenAI-compatible base URL
CUSTOM_LLM_MODEL=          # Model identifier
ARBITRUM_RPC_URL=          # Arbitrum One RPC
ARBITRUM_PRIVATE_KEY=      # Deployment wallet
CIRCLE_API_KEY=            # Circle Agent Stack
ARC_AGENT_WALLET_SEED=     # Arc agent wallets
THE_GRAPH_API_KEY=         # The Graph Network
HEDERA_ACCOUNT_ID=         # Hedera x402
HEDERA_PRIVATE_KEY=        # Hedera x402
```

### Frontend

```bash
cd web
npm install
npm run build
# Serves from web/out/ via nginx
```

### Run Tests

```bash
# Mock pipeline test (no LLM calls)
python3 api/test_pipeline.py

# Live end-to-end test (real LLM calls, ~90 seconds)
python3 api/test_live.py
```

---

## API

```
GET  /api/health                    Agent status + chain
POST /api/cases                     Submit case (JSON)
POST /api/cases/upload              Submit case (file upload)
GET  /api/cases/{case_id}           Retrieve verdict
```

### Submit a Case

```bash
curl -X POST https://api.modusops.xyz/api/cases \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Suspicious wire transfers",
    "documents_text": ["Transaction log: ..."]
  }'
```

---

## Hackathon

Built for [ETHOnline 2026](https://ethglobal.com/events/ethonline2026) and [Arbitrum Open House Singapore Online Buildathon](https://www.hackquest.io/hackathons/Arbitrum-Open-House-Singapore-Online-Buildathon).

Targeting: Arc · The Graph · Hedera · Bazantic · Arbitrum

---

## License

Business Source License 1.1 (BUSL-1.1)

These agents are not yet trained on laws outside the United States. 

© 2026 NthMOMENT. All rights reserved.
