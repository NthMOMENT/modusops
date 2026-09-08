"""LangGraph pipeline wiring the four Modus Ops agents.

Flow:
    law_enforcement -> [prosecutor, defense] (parallel fan-out)
    [prosecutor, defense] -> judge (fan-in, both must complete first)

Day 2: nodes call the real agent invoke() functions, which call the LLM.
"""

import logging
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from api.agents import defense, judge, law_enforcement, prosecutor

logger = logging.getLogger("modusops.agents.pipeline")


class AgentState(TypedDict):
    case_id: str
    documents_text: list[str]
    le_findings: str
    prosecution_brief: Optional[str]
    defense_memorandum: Optional[str]
    verdict: Optional[dict]
    jurisdiction: Optional[str]


def _run_node(name: str, module, state: AgentState) -> dict:
    try:
        return module.invoke(state)
    except Exception as e:
        logger.error("[PIPELINE ERROR] %s: %s", name, e)
        raise


def law_enforcement_node(state: AgentState) -> dict:
    result = _run_node("law_enforcement", law_enforcement, state)
    threading.Thread(target=_pay, args=("law_enforcement", state["case_id"]), daemon=True).start()
    return result


def prosecutor_node(state: AgentState) -> dict:
    result = _run_node("prosecutor", prosecutor, state)
    threading.Thread(target=_pay, args=("da", state["case_id"]), daemon=True).start()
    return result


def defense_node(state: AgentState) -> dict:
    result = _run_node("defense", defense, state)
    threading.Thread(target=_pay, args=("defense", state["case_id"]), daemon=True).start()
    return result


def judge_node(state: AgentState) -> dict:
    result = _run_node("judge", judge, state)
    threading.Thread(target=_pay, args=("judge", state["case_id"]), daemon=True).start()

    verdict_dict = result.get("verdict")
    if verdict_dict:
        try:
            client = _get_chain_client()
            if client:
                tx_hash = client.commit_verdict(verdict_dict)
                verdict_dict["on_chain_tx"] = tx_hash
                logger.info("[CHAIN] case=%s tx=%s", state["case_id"], tx_hash or "n/a")
            else:
                logger.warning("[CHAIN] client disabled — skipping commit for case=%s", state["case_id"])
        except Exception as e:
            logger.error("[CHAIN ERROR] case=%s: %s", state["case_id"], e)

    return result


def build_pipeline():
    graph = StateGraph(AgentState)

    graph.add_node("law_enforcement", law_enforcement_node)
    graph.add_node("prosecutor", prosecutor_node)
    graph.add_node("defense", defense_node)
    graph.add_node("judge", judge_node)

    graph.add_edge(START, "law_enforcement")

    # Parallel fan-out
    graph.add_edge("law_enforcement", "prosecutor")
    graph.add_edge("law_enforcement", "defense")

    # Fan-in: judge waits for both prosecutor and defense
    graph.add_edge("prosecutor", "judge")
    graph.add_edge("defense", "judge")

    graph.add_edge("judge", END)

    return graph.compile()


pipeline = build_pipeline()

# ── Payment integration ───────────────────────────────────────────────────────
from api.chain.payments import get_payment_client as _get_payment_client
from api.chain.commit import get_chain_client as _get_chain_client
import threading

_payment_client = None
_payment_client_lock = threading.Lock()

def _get_client():
    global _payment_client
    with _payment_client_lock:
        if _payment_client is None:
            _payment_client = _get_payment_client()
    return _payment_client

def _pay(agent_role: str, case_id: str) -> None:
    """Fire-and-forget payment — never raises, never blocks pipeline."""
    try:
        client = _get_client()
        if client:
            result = client.pay_agent(agent_role, case_id)
            logger.info("[PAYMENT] %s case=%s tx=%s status=%s",
                        agent_role, case_id,
                        result.get("tx_hash", "n/a"),
                        result.get("status"))
        else:
            logger.warning("[PAYMENT] client disabled — skipping %s", agent_role)
    except Exception as e:
        logger.error("[PAYMENT ERROR] %s: %s", agent_role, e)
