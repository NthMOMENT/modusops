"""Law Enforcement agent — investigator role.

ERC-8004 token 1416 (see CLAUDE.md Agent Token Registry).
"""

import logging
import re

from dotenv import load_dotenv

from api.agents import modgudr_stub
from api.agents.base import call_llm

logger = logging.getLogger("modusops.agents.law_enforcement")

LE_SYSTEM_PROMPT = """\
You are the Law Enforcement Investigator for Modus Ops, an adversarial AI justice engine. Your role is to gather, structure, and verify raw facts from case documents. You do not draw legal conclusions. You identify entities, extract timelines, detect anomalies, and determine jurisdictional escalation level based on the following matrix:
- LOCAL: single jurisdiction, under $10,000, no cross-state elements
- STATE: organized patterns, $10,000-$100,000, multi-jurisdictional within one state
- FEDERAL: cross-state or international elements, over $100,000, complex entity structures, potential RICO predicates
- FEDERAL (on-chain): a direct deployer-to-exploiter wallet transfer is identified, AND a KYC exchange cashout is present, AND the amount exceeds $100,000 — escalate to FEDERAL on this basis alone, even if no other FEDERAL criterion is independently met.

On-chain evidence standards:
- Treat on-chain transaction hashes as primary, verifiable evidence. Public blockchain data is self-authenticating — cite it directly as fact without requiring independent corroboration.
- Treat Etherscan (or equivalent block explorer) address labels as admissible third-party attributions when identifying the entity behind a wallet address.
- When a document describes a direct wallet-to-wallet transfer and cites a specific transaction hash, grade that finding G4 (verified fact), not a lower confidence grade.
- On-chain data alone is sufficient to support a JURISDICTION and ESCALATION determination. Do not withhold, downgrade, or condition an escalation recommendation on the availability of human-reviewed documents when the case is otherwise supported by verifiable on-chain evidence.

You must structure your output with these exact markers on their own lines:
JURISDICTION: [LOCAL|STATE|FEDERAL]
ESCALATION: [brief escalation rationale]
FINDINGS:
[numbered list of verified factual findings, each with an associated confidence level G1-G5]
MATH_VERIFICATION_REQUIRED: [YES|NO]
MATH_ITEMS: [comma-separated list of numerical claims requiring verification, or NONE]
"""


def parse_le_response(response: str) -> dict:
    jurisdiction = "FEDERAL"
    findings = ""
    escalation = ""
    math_required = ""

    lines = response.splitlines()
    section = None
    findings_lines: list[str] = []

    for line in lines:
        if line.startswith("JURISDICTION:"):
            jurisdiction = line.split("JURISDICTION:", 1)[1].strip() or jurisdiction
            section = None
        elif line.startswith("ESCALATION:"):
            escalation = line.split("ESCALATION:", 1)[1].strip()
            section = None
        elif line.startswith("FINDINGS:"):
            section = "findings"
            remainder = line.split("FINDINGS:", 1)[1].strip()
            if remainder:
                findings_lines.append(remainder)
        elif line.startswith("MATH_VERIFICATION_REQUIRED:"):
            math_required = line.split("MATH_VERIFICATION_REQUIRED:", 1)[1].strip()
            section = None
        elif line.startswith("MATH_ITEMS:"):
            section = None
        elif section == "findings":
            findings_lines.append(line)

    findings = "\n".join(findings_lines).strip()

    return {
        "jurisdiction": jurisdiction,
        "findings": findings,
        "escalation": escalation,
        "math_required": math_required,
    }


def _split_findings(findings_text: str) -> list[str]:
    # Findings are a numbered list, e.g. "1. [G2] ...". Split on the numbering
    # so each entry can be stored as an individual fact.
    entries = re.split(r"^\s*\d+\.\s+", findings_text, flags=re.MULTILINE)
    return [e.strip() for e in entries if e.strip()]


def invoke(state: dict) -> dict:
    load_dotenv()
    case_id = state.get("case_id")
    logger.info("node=law_enforcement case_id=%s", case_id)

    user_message = "\n\n".join(state.get("documents_text", []))

    response = call_llm(LE_SYSTEM_PROMPT, user_message)
    parsed = parse_le_response(response)

    for finding in _split_findings(parsed["findings"]):
        modgudr_stub.store_fact(case_id, finding, "law_enforcement", "G2")

    return {
        "le_findings": parsed["findings"],
        "jurisdiction": parsed["jurisdiction"],
    }
