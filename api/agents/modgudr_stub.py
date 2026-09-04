"""Placeholder for Modgudr, the local proprietary case-memory MCP
(see CLAUDE.md Security Protocol — modgudr/ itself is gitignored and never
committed). This stub lets agent code integrate against the real interface
before Modgudr is connected.
"""

import logging

logger = logging.getLogger("modusops.agents.modgudr_stub")


def store_fact(case_id: str, fact: str, agent_role: str, grade: str) -> dict:
    logger.info("[MODGUDR STUB] store_fact called for case %s", case_id)
    return {
        "stored": True,
        "grade": grade,
        "fact_id": f"{case_id}-{hash(fact) % 10000}",
        "method": "stub",
    }


def recall_facts(case_id: str) -> list:
    logger.info("[MODGUDR STUB] recall_facts called for case %s", case_id)
    return []


def verify_fact(fact_id: str, new_evidence: str) -> dict:
    logger.info("[MODGUDR STUB] verify_fact called for case %s", fact_id)
    return {
        "verified": False,
        "method": "stub",
        "note": "Modgudr not connected",
    }
