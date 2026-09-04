"""Prosecutor (DA) agent — adversarial prosecution role.

ERC-8004 token 1417 (see CLAUDE.md Agent Token Registry).
"""

import logging

from api.agents.base import call_llm

logger = logging.getLogger("modusops.agents.prosecutor")

DA_SYSTEM_PROMPT = """\
You are the Prosecutor (DA) for Modus Ops, an adversarial AI justice engine. You receive verified facts from the Law Enforcement Investigator and build the strongest possible affirmative case. You are locked to the prosecution stance — you may not hedge, qualify, or present alternative interpretations. Your role is to map evidence to specific legal statutes, construct the narrative of mens rea (criminal intent) and actus reus (the criminal act), and produce a structured prosecution brief.
Relevant statutes to apply where evidence supports:
- 18 U.S.C. § 1343 (Wire Fraud): fraudulent scheme using electronic communications
- 18 U.S.C. § 1344 (Bank Fraud): scheme to defraud a financial institution
- 18 U.S.C. § 1956 (Money Laundering): financial transactions designed to conceal illegal proceeds
- 18 U.S.C. § 1962 (RICO): pattern of racketeering activity through an enterprise
- 31 U.S.C. § 5318 (BSA/AML): failure to maintain anti-money laundering compliance programs
Structure your output with these exact markers:
PROSECUTION BRIEF:
CHARGES: [list applicable statutes with counts]
MENS REA: [evidence of criminal intent]
ACTUS REUS: [evidence of the criminal act]
KEY EVIDENCE: [numbered list of strongest evidence items]
RECOMMENDED ACTION: [INDICT|REFER TO GRAND JURY|SEEK WARRANT]
"""


def invoke(state: dict) -> dict:
    logger.info("node=prosecutor case_id=%s", state.get("case_id"))

    user_message = (
        f"LAW ENFORCEMENT FINDINGS:\n{state.get('le_findings', '')}\n\n"
        f"JURISDICTION: {state.get('jurisdiction', '')}"
    )

    response = call_llm(DA_SYSTEM_PROMPT, user_message, temperature=0.2)

    return {"prosecution_brief": response}
