"""Placeholder for the Math MCP (x402-gated, Hedera rail) numerical
verification tool. The real Math MCP is proprietary and gitignored
(see CLAUDE.md Security Protocol) — this stub flags numerical claims for
manual verification until it's connected.
"""


def verify_numbers(data: str) -> dict:
    return {
        "verified": False,
        "method": "stub",
        "note": "Math MCP not connected — numerical claims flagged for manual verification",
        "flagged_items": data,
    }
