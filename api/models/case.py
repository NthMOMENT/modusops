from typing import Literal, Optional

from pydantic import BaseModel

from api.models.verdict import Finding, VerdictObject


class CaseState(BaseModel):
    case_id: str
    status: Literal[
        "INGESTING",
        "INVESTIGATING",
        "DELIBERATING",
        "ADJUDICATING",
        "COMPLETE",
        "FAILED",
    ]
    documents_text: list[str] = []
    findings: list[Finding] = []
    verdict: Optional[VerdictObject] = None
    created_at: int
    updated_at: int
