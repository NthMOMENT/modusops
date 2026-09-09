import logging
import uuid
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api import db
from api.agents.pipeline import pipeline
from api.ingestion import extract_text_from_upload
from api.models.verdict import VerdictObject

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modusops.api")

app = FastAPI(title="Modus Ops API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://modusops.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


class CaseRequest(BaseModel):
    case_id: Optional[str] = None
    description: str
    documents_text: list[str] = []


def _run_case(case_id: str, documents_text: list[str]):
    logger.info("running case case_id=%s", case_id)

    initial_state = {
        "case_id": case_id,
        "documents_text": documents_text,
        "le_findings": "",
        "prosecution_brief": "",
        "defense_memorandum": "",
        "verdict": None,
        "jurisdiction": "FEDERAL",
    }

    try:
        result = pipeline.invoke(initial_state)
    except Exception as e:
        logger.error("[PIPELINE ERROR] case_id=%s: %s", case_id, e)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "case_id": case_id},
        )

    verdict_obj = VerdictObject(**result["verdict"])

    logger.info(
        "[DB] saving verdict case_id=%s verdict=%s confidence_score=%s",
        verdict_obj.case_id, verdict_obj.verdict, verdict_obj.confidence_score,
    )
    try:
        db.save_verdict(verdict_obj)
    except Exception:
        logger.exception("[DB ERROR] failed to save verdict case_id=%s", verdict_obj.case_id)
        raise
    logger.info("[DB] save complete case_id=%s", verdict_obj.case_id)

    return verdict_obj


@app.post("/api/cases", response_model=VerdictObject)
def create_case(request: CaseRequest):
    case_id = request.case_id or str(uuid.uuid4())
    return _run_case(case_id, request.documents_text)


@app.post("/api/cases/upload", response_model=VerdictObject)
async def create_case_upload(files: list[UploadFile] = File(...), description: str = Form(...)):
    case_id = str(uuid.uuid4())

    documents_text = []
    for file in files:
        file_bytes = await file.read()
        documents_text.append(extract_text_from_upload(file_bytes, file.filename))

    return _run_case(case_id, documents_text)


@app.get("/api/cases", response_model=list[VerdictObject])
def list_cases():
    return db.list_verdicts()


@app.get("/api/cases/{case_id}", response_model=VerdictObject)
def get_case(case_id: str):
    verdict = db.get_verdict(case_id)
    if verdict is None:
        raise HTTPException(status_code=404, detail="case not found")
    return verdict


@app.get("/api/cases/{case_id}/verdict", response_model=VerdictObject)
def get_case_verdict(case_id: str):
    verdict = db.get_verdict(case_id)
    if verdict is None:
        raise HTTPException(status_code=404, detail="case not found")
    return verdict


@app.get("/api/cases/{case_id}/status")
def get_case_status(case_id: str):
    verdict = db.get_verdict(case_id)
    if verdict is None:
        return {
            "case_id": case_id,
            "status": "running",
            "steps": {
                "law_enforcement": "pending",
                "prosecutor": "pending",
                "defense": "pending",
                "judge": "pending",
            },
        }

    return {
        "case_id": case_id,
        "status": "complete",
        "steps": {
            "law_enforcement": "done",
            "prosecutor": "done",
            "defense": "done",
            "judge": "done",
        },
        "jurisdiction": verdict.jurisdiction,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "agents": 4, "chain": "arbitrum-one"}
