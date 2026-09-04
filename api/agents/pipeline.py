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
    return _run_node("law_enforcement", law_enforcement, state)


def prosecutor_node(state: AgentState) -> dict:
    return _run_node("prosecutor", prosecutor, state)


def defense_node(state: AgentState) -> dict:
    return _run_node("defense", defense, state)


def judge_node(state: AgentState) -> dict:
    return _run_node("judge", judge, state)


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
