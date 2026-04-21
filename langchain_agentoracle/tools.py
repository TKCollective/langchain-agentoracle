"""
LangChain tools for AgentOracle — trust verification for LangChain agents.

All endpoints, full error handling, 402 payment awareness, retry logic.
Mirrors the crewai-agentoracle tool surface so integration tutorials
read the same across frameworks.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Type

import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

AGENTORACLE_BASE_URL = "https://agentoracle.co"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 3
RETRY_BACKOFF = 2


# ─────────────────────────────────────────────────────────────────────
#  Core HTTP with retry + 402/429/500 handling
# ─────────────────────────────────────────────────────────────────────
def _make_request(
    endpoint: str,
    payload: Dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    url = f"{AGENTORACLE_BASE_URL}{endpoint}"
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.post(
                url, json=payload, timeout=timeout,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            if response.status_code == 402:
                return {
                    "success": False, "error": "payment_required",
                    "message": (
                        "This endpoint requires x402 payment (USDC on Base). "
                        "Use /preview for free access, or configure an x402 "
                        "wallet. See: agentoracle.co/.well-known/x402.json"
                    ),
                    "payment_info": response.json() if response.text else {},
                }
            if response.status_code == 429:
                retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
                return {
                    "success": False, "error": "rate_limited",
                    "message": f"Rate limit exceeded. Resets in {retry_after}s.",
                    "retry_after": retry_after,
                }
            if response.status_code >= 500 and attempt < retries - 1:
                time.sleep(RETRY_BACKOFF ** attempt)
                continue
            return {
                "success": False, "error": f"http_{response.status_code}",
                "message": response.text[:500],
            }
        except requests.Timeout:
            last_error = "Request timed out"
            if attempt < retries - 1:
                time.sleep(RETRY_BACKOFF ** attempt); continue
        except requests.ConnectionError:
            last_error = "Connection failed — check network or agentoracle.co"
            if attempt < retries - 1:
                time.sleep(RETRY_BACKOFF ** attempt); continue
        except Exception as e:
            return {"success": False, "error": "unexpected", "message": str(e)}
    return {"success": False, "error": "max_retries", "message": last_error}


# ─────────────────────────────────────────────────────────────────────
#  Formatters
# ─────────────────────────────────────────────────────────────────────
def _format_evaluation(data: Dict[str, Any]) -> str:
    ev = data.get("evaluation", {})
    if not ev:
        return f"Evaluation error: {data}"
    lines = [
        "EVALUATION RESULT",
        f"Overall confidence: {ev.get('overall_confidence', 0):.2f}",
        f"Recommendation: {ev.get('recommendation', 'unknown').upper()}",
        f"Claims found: {ev.get('total_claims', 0)} | "
        f"Supported: {ev.get('verified_claims', 0)} | "
        f"Refuted: {ev.get('refuted_claims', 0)} | "
        f"Unverifiable: {ev.get('unverifiable_claims', 0)}",
        f"Sources used: {', '.join(ev.get('sources_used', []))}",
        "", "CLAIMS:",
    ]
    for c in ev.get("claims", []):
        verdict = c.get("verdict", "unknown")
        mark = {"supported": "✓", "refuted": "✗", "unverifiable": "?"}.get(verdict, "?")
        lines.append(
            f"  {mark} [{verdict.upper()}] ({c.get('confidence', 0):.2f}) {c.get('claim', '')}"
        )
        if c.get("evidence"):
            lines.append(f"    Evidence: {c['evidence'][:200]}")
        if c.get("correction"):
            lines.append(f"    Correction: {c['correction']}")
    return "\n".join(lines)


def _format_verify_gate(data: Dict[str, Any]) -> str:
    lines = [
        f"VERIFY GATE: {'PASS' if data.get('pass') else 'FAIL'}",
        f"Confidence: {data.get('confidence', 0):.2f}",
        f"Min required: {data.get('min_confidence_required', 0):.2f}",
        f"Recommendation: {data.get('recommendation', 'unknown').upper()}",
        f"Adversarial pass: {data.get('adversarial_pass', 'unknown')}",
    ]
    return "\n".join(lines)


def _format_preview(data: Dict[str, Any]) -> str:
    result = data.get("result", {})
    summary = (result.get("summary") or "")[:400]
    facts = result.get("key_facts", [])[:3]
    score = result.get("confidence_score", 0)
    lines = [
        "PREVIEW (free, truncated):",
        f"Summary: {summary}",
        f"Confidence: {score:.2f}",
    ]
    if facts:
        lines.append("Key facts:")
        for f in facts:
            lines.append(f"  • {str(f)[:150]}")
    lines.append("\n(Call AgentOracleResearchTool for full results — $0.02 USDC)")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
#  Tool: evaluate — per-claim verification ($0.02, returns free in beta)
# ─────────────────────────────────────────────────────────────────────
class _EvaluateInput(BaseModel):
    content: str = Field(description="Text containing claims to verify")
    min_confidence: float = Field(default=0.8, description="Confidence threshold (0-1)")


class AgentOracleEvaluateTool(BaseTool):
    """Per-claim verification. Returns verdict, confidence, evidence, corrections."""
    name: str = "agentoracle_evaluate"
    description: str = (
        "Verify claims in a block of text. Returns per-claim verdicts "
        "(supported/refuted/unverifiable) with confidence scores, evidence, "
        "and corrections. Use BEFORE acting on any LLM-generated output."
    )
    args_schema: Type[BaseModel] = _EvaluateInput
    min_confidence: float = 0.8

    def _run(self, content: str, min_confidence: Optional[float] = None) -> str:
        payload = {"content": content, "min_confidence": min_confidence or self.min_confidence}
        r = _make_request("/evaluate", payload)
        if not r["success"]:
            return f"Evaluation error ({r['error']}): {r['message']}"
        return _format_evaluation(r["data"])


# ─────────────────────────────────────────────────────────────────────
#  Tool: verify-gate — fast pass/fail gate (free, beta)
# ─────────────────────────────────────────────────────────────────────
class _VerifyGateInput(BaseModel):
    content: str = Field(description="Text to gate-check for factual soundness")
    min_confidence: float = Field(default=0.5)


class AgentOracleVerifyGateTool(BaseTool):
    """Fast pass/fail gate. Use when you only need a binary decision, not per-claim breakdowns."""
    name: str = "agentoracle_verify_gate"
    description: str = (
        "Fast binary gate. Returns PASS/FAIL with confidence. Use this when "
        "you only need to decide whether to proceed, not a full breakdown."
    )
    args_schema: Type[BaseModel] = _VerifyGateInput
    min_confidence: float = 0.5

    def _run(self, content: str, min_confidence: Optional[float] = None) -> str:
        payload = {"content": content, "min_confidence": min_confidence or self.min_confidence}
        r = _make_request("/verify-gate", payload)
        if not r["success"]:
            return f"Verify-gate error ({r['error']}): {r['message']}"
        return _format_verify_gate(r["data"])


# ─────────────────────────────────────────────────────────────────────
#  Tool: preview — free research preview (10/hr)
# ─────────────────────────────────────────────────────────────────────
class _PreviewInput(BaseModel):
    query: str = Field(description="Research question (natural language)")


class AgentOraclePreviewTool(BaseTool):
    """Free truncated research preview. 10 requests/hour. No payment required."""
    name: str = "agentoracle_preview"
    description: str = (
        "Free research preview — truncated summary, a few key facts, "
        "and a confidence score. 10 requests/hour. No payment required."
    )
    args_schema: Type[BaseModel] = _PreviewInput

    def _run(self, query: str) -> str:
        r = _make_request("/preview", {"query": query})
        if not r["success"]:
            return f"Preview error ({r['error']}): {r['message']}"
        return _format_preview(r["data"])


# ─────────────────────────────────────────────────────────────────────
#  Tool: research — paid research ($0.02 USDC on Base)
# ─────────────────────────────────────────────────────────────────────
class _ResearchInput(BaseModel):
    query: str = Field(description="Research question")
    tier: str = Field(default="standard", description="standard or deep")


class AgentOracleResearchTool(BaseTool):
    """Paid research. Requires x402 payment (USDC on Base)."""
    name: str = "agentoracle_research"
    description: str = (
        "Full research (paid: $0.02 USDC on Base). Returns summary, key facts, "
        "sources, and confidence. For free access use AgentOraclePreviewTool."
    )
    args_schema: Type[BaseModel] = _ResearchInput

    def _run(self, query: str, tier: str = "standard") -> str:
        r = _make_request("/research", {"query": query, "tier": tier})
        if not r["success"]:
            # Friendly 402 explanation for agent logs
            return f"Research error ({r['error']}): {r['message']}"
        return str(r["data"])


# ─────────────────────────────────────────────────────────────────────
#  Backwards compat: AgentOracleTool (v0.1 shipped this — keep .run())
# ─────────────────────────────────────────────────────────────────────
class AgentOracleTool(AgentOraclePreviewTool):
    """Legacy name for AgentOraclePreviewTool — kept for v0.1 compatibility."""
    name: str = "agentoracle_research"

    def invoke(self, data: Dict[str, Any]) -> str:  # type: ignore[override]
        if isinstance(data, dict) and "query" in data:
            return self._run(query=data["query"])
        return super().invoke(data)


# ─────────────────────────────────────────────────────────────────────
#  Convenience bundle
# ─────────────────────────────────────────────────────────────────────
def get_agentoracle_tools(include_paid: bool = False) -> List[BaseTool]:
    """All AgentOracle tools ready for a LangChain agent. include_paid=True adds /research."""
    tools: List[BaseTool] = [
        AgentOracleEvaluateTool(),
        AgentOracleVerifyGateTool(),
        AgentOraclePreviewTool(),
    ]
    if include_paid:
        tools.append(AgentOracleResearchTool())
    return tools


__all__ = [
    "AgentOracleTool",
    "AgentOracleEvaluateTool",
    "AgentOracleVerifyGateTool",
    "AgentOraclePreviewTool",
    "AgentOracleResearchTool",
    "get_agentoracle_tools",
]
