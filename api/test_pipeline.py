"""Smoke test for the agent pipeline with the LLM call mocked out.

Run directly: python3 api/test_pipeline.py
"""

import json
import os
import sys
from unittest import mock

# Allow `python3 api/test_pipeline.py` to resolve the `api` package when run
# directly (not as `python3 -m api.test_pipeline`).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LE_RESPONSE = (
    "JURISDICTION: FEDERAL\n"
    "ESCALATION: Cross-state wire transfers over $100k\n"
    "FINDINGS:\n"
    "1. [G2] Entity XYZ LLC received $248,500 in 3 transactions\n"
    "MATH_VERIFICATION_REQUIRED: YES\n"
    "MATH_ITEMS: $248,500 total"
)

DA_RESPONSE = (
    "PROSECUTION BRIEF:\n"
    "CHARGES: 18 U.S.C. § 1343 Wire Fraud (Count I)\n"
    "MENS REA: Pattern of structured payments\n"
    "ACTUS REUS: Electronic transfers across state lines\n"
    "KEY EVIDENCE:\n"
    "1. Transaction records\n"
    "RECOMMENDED ACTION: INDICT"
)

DEFENSE_RESPONSE = (
    "DEFENSE MEMORANDUM:\n"
    "REASONABLE DOUBT: 1. No direct evidence of intent\n"
    "CHAIN OF CUSTODY ISSUES: 1. Bank statement lacks certification\n"
    "DAUBERT CHALLENGES: 1. Statistical baseline not established\n"
    "EXCULPATORY EVIDENCE: 1. Legitimate business invoices present\n"
    "MOTIONS: Motion to Suppress uncertified documents\n"
    "DEFENSE RECOMMENDATION: SEEK PLEA"
)

JUDGE_RESPONSE = (
    "VERDICT: PROCEED\n"
    "CONFIDENCE: 74\n"
    "JURISDICTION_CONFIRMED: FEDERAL\n"
    "JUDICIAL SUMMARY:\n"
    "The evidence presented supports proceeding. While defense raises valid chain-of-custody "
    "concerns, the mathematical evidence of structured payments is compelling.\n"
    "EVIDENTIARY GAPS:\n"
    "1. Original certified bank statement required"
)


def fake_call_llm(system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
    # Checked most-specific-first: JUDGE_SYSTEM_PROMPT references "the Law
    # Enforcement findings" and DEFENSE_SYSTEM_PROMPT references "the
    # Prosecutor", so a naive Law-Enforcement-first / Prosecutor-first check
    # would misroute those prompts to the wrong canned response.
    if "Judge" in system_prompt:
        return JUDGE_RESPONSE
    if "Defense" in system_prompt:
        return DEFENSE_RESPONSE
    if "Prosecutor" in system_prompt:
        return DA_RESPONSE
    if "Law Enforcement" in system_prompt:
        return LE_RESPONSE
    raise ValueError("unrecognized system prompt in fake_call_llm")


def run_smoke_test():
    # Each agent module did `from api.agents.base import call_llm`, so the
    # name must be patched in every module that imported it, not just in
    # api.agents.base.
    with mock.patch("api.agents.base.call_llm", side_effect=fake_call_llm), \
         mock.patch("api.agents.law_enforcement.call_llm", side_effect=fake_call_llm), \
         mock.patch("api.agents.prosecutor.call_llm", side_effect=fake_call_llm), \
         mock.patch("api.agents.defense.call_llm", side_effect=fake_call_llm), \
         mock.patch("api.agents.judge.call_llm", side_effect=fake_call_llm):
        from api.agents.pipeline import pipeline

        state = {
            "case_id": "TEST-001",
            "documents_text": [
                "Suspicious loan application. Amount: $248,500. Entities: XYZ LLC, ABC Corp. "
                "Cross-state transactions detected."
            ],
            "le_findings": "",
            "prosecution_brief": "",
            "defense_memorandum": "",
            "verdict": None,
            "jurisdiction": "FEDERAL",
        }

        result = pipeline.invoke(state)

    verdict = result["verdict"]

    assert verdict["verdict"] == "PROCEED", f"expected PROCEED, got {verdict['verdict']}"
    assert verdict["confidence_score"] == 74, f"expected 74, got {verdict['confidence_score']}"
    assert verdict["jurisdiction"] == "FEDERAL", f"expected FEDERAL, got {verdict['jurisdiction']}"
    assert len(verdict["evidence_hashes"]) == 3, (
        f"expected 3 evidence hashes, got {len(verdict['evidence_hashes'])}"
    )

    print("SMOKE TEST PASSED")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    run_smoke_test()
