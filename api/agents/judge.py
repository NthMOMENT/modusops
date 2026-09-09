"""Judge agent — impartial arbiter role.

ERC-8004 token 1419 (see CLAUDE.md Agent Token Registry).
"""

import hashlib
import logging
import re
import time

from api.agents.base import call_llm
from api.models.verdict import VerdictObject

logger = logging.getLogger("modusops.agents.judge")

AGENT_TOKENS = {
    "law_enforcement": 1416,
    "prosecutor": 1417,
    "defense": 1418,
    "judge": 1419,
}

JUDGE_SYSTEM_PROMPT = """\
You are the Presiding Judge for Modus Ops, an adversarial AI justice engine. You receive the full adversarial record — the Law Enforcement findings, the Prosecution Brief, and the Defense Memorandum — and you adjudicate. You are strictly impartial. You evaluate logical consistency, procedural fairness, strength of evidence, and the quality of adversarial arguments on both sides. You cannot issue a verdict without reviewing both the prosecution and defense submissions.
Issue a confidence score from 0-100 representing your confidence that the evidence supports proceeding with prosecution (0 = dismiss, 100 = proceed with certainty).
Issue one of four verdicts:
- PROCEED: evidence is strong, prosecution should move forward
- DISMISS: insufficient evidence or fatal procedural defects
- ESCALATE: case requires higher jurisdiction or additional investigation
- REVIEW: evidentiary gaps require human review before proceeding
Structure your output with these exact markers:
VERDICT: [PROCEED|DISMISS|ESCALATE|REVIEW]
CONFIDENCE: [0-100]
JURISDICTION_CONFIRMED: [LOCAL|STATE|FEDERAL]
JUDICIAL SUMMARY:
[2-3 paragraph summary of your reasoning, acknowledging the strongest arguments on both sides]
EVIDENTIARY GAPS:
[numbered list of facts requiring human verification before this verdict can be acted upon]
"""


CONFIDENCE_RE = re.compile(r"confidence\s*:\**\s*(-?\d+)", re.IGNORECASE)
VALID_VERDICTS = {"PROCEED", "DISMISS", "ESCALATE", "REVIEW"}
VALID_JURISDICTIONS = {"LOCAL", "STATE", "FEDERAL"}


def _strip_markdown(line: str) -> str:
    return line.strip().lstrip("*#- ").rstrip("*")


def parse_judge_response(response: str, state: dict) -> dict:
    verdict = "REVIEW"
    confidence = 50
    confidence_found = False
    jurisdiction = state.get("jurisdiction", "FEDERAL")
    summary_lines: list[str] = []

    lines = response.splitlines()
    section = None

    for raw_line in lines:
        line = _strip_markdown(raw_line)
        line_upper = line.upper()

        if line_upper.startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip().strip("*").strip().upper()
            section = None
        elif line_upper.startswith("CONFIDENCE:"):
            match = CONFIDENCE_RE.search(line)
            if match:
                confidence = max(0, min(100, int(match.group(1))))
                confidence_found = True
            else:
                logger.warning(
                    "node=judge case_id=%s could not parse CONFIDENCE from line=%r — defaulting to %d",
                    state.get("case_id"), raw_line, confidence,
                )
            section = None
        elif line_upper.startswith("JURISDICTION_CONFIRMED:"):
            jurisdiction = line.split(":", 1)[1].strip().strip("*").strip().upper() or jurisdiction
            section = None
        elif line_upper.startswith("JUDICIAL SUMMARY:"):
            section = "summary"
            remainder = line.split(":", 1)[1].strip()
            if remainder:
                summary_lines.append(remainder)
        elif line_upper.startswith("EVIDENTIARY GAPS:"):
            section = None
        elif section == "summary":
            summary_lines.append(raw_line)

    if not confidence_found:
        logger.warning(
            "node=judge case_id=%s no CONFIDENCE line found in judge response — defaulting to %d",
            state.get("case_id"), confidence,
        )
    if verdict not in VALID_VERDICTS:
        logger.warning(
            "node=judge case_id=%s unrecognized verdict=%r — defaulting to REVIEW",
            state.get("case_id"), verdict,
        )
        verdict = "REVIEW"
    if jurisdiction not in VALID_JURISDICTIONS:
        logger.warning(
            "node=judge case_id=%s unrecognized jurisdiction=%r — defaulting to FEDERAL",
            state.get("case_id"), jurisdiction,
        )
        jurisdiction = "FEDERAL"
    logger.info(
        "node=judge case_id=%s parsed verdict=%s confidence_score=%d",
        state.get("case_id"), verdict, confidence,
    )

    judicial_summary = "\n".join(summary_lines).strip()

    le_findings = state.get("le_findings", "") or ""
    prosecution_brief = state.get("prosecution_brief", "") or ""
    defense_memorandum = state.get("defense_memorandum", "") or ""

    verdict_obj = VerdictObject(
        case_id=state["case_id"],
        timestamp=int(time.time()),
        verdict=verdict,
        confidence_score=confidence,
        jurisdiction=jurisdiction,
        prosecution_brief=prosecution_brief,
        defense_memorandum=defense_memorandum,
        judicial_summary=judicial_summary,
        evidence_hashes=[
            hashlib.sha256(le_findings.encode("utf-8")).hexdigest(),
            hashlib.sha256(prosecution_brief.encode("utf-8")).hexdigest(),
            hashlib.sha256(defense_memorandum.encode("utf-8")).hexdigest(),
        ],
        agent_tokens=AGENT_TOKENS,
        on_chain_tx=None,
    )

    return verdict_obj.model_dump()


def invoke(state: dict) -> dict:
    logger.info("node=judge case_id=%s", state.get("case_id"))

    user_message = (
        f"LAW ENFORCEMENT FINDINGS:\n{state.get('le_findings', '')}\n\n"
        f"PROSECUTION BRIEF:\n{state.get('prosecution_brief', '')}\n\n"
        f"DEFENSE MEMORANDUM:\n{state.get('defense_memorandum', '')}"
    )

    response = call_llm(JUDGE_SYSTEM_PROMPT, user_message, temperature=0.1)
    verdict_dict = parse_judge_response(response, state)

    return {"verdict": verdict_dict}
