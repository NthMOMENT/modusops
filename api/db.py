import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from api.models.verdict import VerdictObject

logger = logging.getLogger("modusops.db")

# Absolute path anchored to this file's location — independent of the
# process's CWD, so it resolves the same whether uvicorn is launched from
# ~/modusops or ~/modusops/api.
DB_PATH = Path(__file__).parent / "cases.db"
DATABASE_URL = f"sqlite:///{DB_PATH.resolve()}"

logger.info("[DB] resolved database path: %s", DB_PATH.resolve())
print(f"[DB] resolved database path: {DB_PATH.resolve()}", flush=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String, primary_key=True)
    timestamp = Column(Integer, nullable=False)
    verdict = Column(String, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    jurisdiction = Column(String, nullable=False)
    prosecution_brief = Column(Text, nullable=False)
    defense_memorandum = Column(Text, nullable=False)
    judicial_summary = Column(Text, nullable=False)
    evidence_hashes = Column(Text, nullable=False)  # JSON-encoded list[str]
    agent_tokens = Column(Text, nullable=False)  # JSON-encoded dict
    on_chain_tx = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def _row_to_verdict(row: Case) -> VerdictObject:
    return VerdictObject(
        case_id=row.case_id,
        timestamp=row.timestamp,
        verdict=row.verdict,
        confidence_score=row.confidence_score,
        jurisdiction=row.jurisdiction,
        prosecution_brief=row.prosecution_brief,
        defense_memorandum=row.defense_memorandum,
        judicial_summary=row.judicial_summary,
        evidence_hashes=json.loads(row.evidence_hashes),
        agent_tokens=json.loads(row.agent_tokens),
        on_chain_tx=row.on_chain_tx,
    )


def save_verdict(verdict: VerdictObject) -> None:
    session: Session = SessionLocal()
    try:
        row = session.get(Case, verdict.case_id)
        if row is None:
            row = Case(case_id=verdict.case_id)
            session.add(row)

        row.timestamp = verdict.timestamp
        row.verdict = verdict.verdict
        row.confidence_score = verdict.confidence_score
        row.jurisdiction = verdict.jurisdiction
        row.prosecution_brief = verdict.prosecution_brief
        row.defense_memorandum = verdict.defense_memorandum
        row.judicial_summary = verdict.judicial_summary
        row.evidence_hashes = json.dumps(verdict.evidence_hashes)
        row.agent_tokens = json.dumps(verdict.agent_tokens)
        row.on_chain_tx = verdict.on_chain_tx

        session.commit()
    finally:
        session.close()


def get_verdict(case_id: str) -> Optional[VerdictObject]:
    session: Session = SessionLocal()
    try:
        row = session.get(Case, case_id)
        if row is None:
            return None
        return _row_to_verdict(row)
    finally:
        session.close()


def list_verdicts() -> list[VerdictObject]:
    session: Session = SessionLocal()
    try:
        rows = session.query(Case).order_by(Case.timestamp.desc()).all()
        return [_row_to_verdict(row) for row in rows]
    finally:
        session.close()


def case_exists(case_id: str) -> bool:
    session: Session = SessionLocal()
    try:
        return session.get(Case, case_id) is not None
    finally:
        session.close()
