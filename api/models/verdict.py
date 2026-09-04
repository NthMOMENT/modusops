from typing import Literal, Optional

from pydantic import BaseModel


class CaseInput(BaseModel):
    case_id: str
    description: str


class Finding(BaseModel):
    finding_id: str
    agent_role: str
    content: str
    confidence: int
    evidence_hash: str
    grade: Literal["G1", "G2", "G3", "G4", "G5"]


class VerdictObject(BaseModel):
    case_id: str
    timestamp: int
    verdict: Literal["PROCEED", "DISMISS", "ESCALATE", "REVIEW"]
    confidence_score: int
    jurisdiction: Literal["LOCAL", "STATE", "FEDERAL"]
    prosecution_brief: str
    defense_memorandum: str
    judicial_summary: str
    evidence_hashes: list[str]
    agent_tokens: dict
    on_chain_tx: Optional[str] = None
