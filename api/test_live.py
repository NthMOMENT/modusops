"""Live end-to-end pipeline test — makes REAL LLM calls, no mocking.

Run directly: python3 api/test_live.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402

VALID_VERDICTS = {"PROCEED", "DISMISS", "ESCALATE", "REVIEW"}


def run_live_test():
    load_dotenv()

    if not os.getenv("CUSTOM_LLM_API_KEY") or not os.getenv("CUSTOM_LLM_BASE_URL"):
        print(
            "SKIPPED: CUSTOM_LLM_API_KEY / CUSTOM_LLM_BASE_URL not set — "
            "cannot make live LLM calls."
        )
        return

    from api.agents.pipeline import pipeline

    documents_text = [
        "SUSPICIOUS ACTIVITY REPORT — CASE REF: SAR-2026-0001\n\n"
        "Subject: XYZ Consulting LLC\n"
        "Date Range: Jan 2026 - Aug 2026\n\n"
        "Transaction Summary:\n"
        "- Jan 15: Wire transfer $82,500 from XYZ LLC (Delaware) to ABC Holdings (Nevada)\n"
        "- Mar 3: Wire transfer $91,000 from XYZ LLC (Delaware) to ABC Holdings (Nevada)\n"
        "- Jun 18: Wire transfer $75,000 from XYZ LLC (Delaware) to Offshore account "
        "(Cayman Islands)\n"
        "Total: $248,500 across 3 transactions\n\n"
        "Anomalies Detected:\n"
        "- All transfers occurred within 3 days of quarterly tax filing deadlines\n"
        "- ABC Holdings registered 6 months ago, no public business activity\n"
        "- Cayman Islands account opened same month as first transaction\n"
        "- No invoices or contracts found to justify transfers"
    ]

    state = {
        "case_id": "LIVE-TEST-001",
        "documents_text": documents_text,
        "le_findings": "",
        "prosecution_brief": "",
        "defense_memorandum": "",
        "verdict": None,
        "jurisdiction": "FEDERAL",
    }

    try:
        result = pipeline.invoke(state)
        verdict = result["verdict"]

        print(json.dumps(verdict, indent=2))

        assert verdict["verdict"] in VALID_VERDICTS, (
            f"verdict {verdict['verdict']!r} not in {VALID_VERDICTS}"
        )
        assert 0 <= verdict["confidence_score"] <= 100, (
            f"confidence_score {verdict['confidence_score']} out of range"
        )
        assert len(verdict["evidence_hashes"]) == 3, (
            f"expected 3 evidence hashes, got {len(verdict['evidence_hashes'])}"
        )

        print("LIVE TEST PASSED")
    except Exception as e:
        print(f"LIVE TEST FAILED: {e}")
        raise


if __name__ == "__main__":
    run_live_test()
