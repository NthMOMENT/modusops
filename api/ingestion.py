"""Document text extraction for the Law Enforcement ingestion layer.

Supports PDF (via unstructured), plain text, CSV, and JSON. Anything else
falls back to a best-effort UTF-8 decode, or a placeholder note if the
content isn't text at all.
"""

import base64
import json
import logging
import os
import tempfile

from unstructured.partition.pdf import partition_pdf

logger = logging.getLogger("modusops.ingestion")


def _extract(file_bytes: bytes, filename: str) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(file_bytes)
            elements = partition_pdf(filename=temp_path)
            return "\n".join(str(el) for el in elements)
        finally:
            os.remove(temp_path)

    if lower.endswith(".txt") or lower.endswith(".csv"):
        return file_bytes.decode("utf-8")

    if lower.endswith(".json"):
        return json.dumps(json.loads(file_bytes.decode("utf-8")), indent=2)

    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return f"[Binary file — could not extract text: {filename}]"


def extract_text_from_base64(b64_string: str, filename: str) -> str:
    file_bytes = base64.b64decode(b64_string)
    text = _extract(file_bytes, filename)
    logger.info("[INGESTION] extracted %d chars from %s", len(text), filename)
    return text


def extract_text_from_upload(file_bytes: bytes, filename: str) -> str:
    text = _extract(file_bytes, filename)
    logger.info("[INGESTION] extracted %d chars from %s", len(text), filename)
    return text
