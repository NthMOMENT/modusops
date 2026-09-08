"""Shared LLM client for all Modus Ops agent nodes.

This is the ONLY module in the codebase permitted to reference the
CUSTOM_LLM_MODEL env var. Per CLAUDE.md, the underlying model name/ID must
never be hardcoded, logged, or disclosed elsewhere — publicly and in code
comments it is referred to only as "custom LLM".
"""

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger("modusops.agents.base")

# Suppress httpx request logging — it prints the full request URL, which
# would leak the LLM provider's domain into logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx2").setLevel(logging.WARNING)

_REQUIRED_ENV_VARS = ("CUSTOM_LLM_BASE_URL", "CUSTOM_LLM_API_KEY", "CUSTOM_LLM_MODEL")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(
            f"{name} is not set — required env vars are {_REQUIRED_ENV_VARS}. "
            "Set them in api/.env (see .env.example)."
        )
    return value


def get_llm_client() -> OpenAI:
    load_dotenv('/root/modusops/api/.env')
    base_url = _require_env("CUSTOM_LLM_BASE_URL")
    api_key = _require_env("CUSTOM_LLM_API_KEY")
    return OpenAI(base_url=base_url, api_key=api_key)


def get_model_id() -> str:
    load_dotenv('/root/modusops/api/.env')
    return _require_env("CUSTOM_LLM_MODEL")


def call_llm(system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
    client = get_llm_client()
    model = get_model_id()

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=384000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    usage = response.usage
    tokens_used = usage.total_tokens if usage else "unknown"
    logger.info("[LLM] call complete, tokens used: %s", tokens_used)

    return response.choices[0].message.content
