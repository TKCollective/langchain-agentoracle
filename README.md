# langchain-agentoracle

**Trust verification for LangChain agents. Per-claim. Before they act.**

Your LangChain agent retrieves data and acts on it. But retrieval doesn't mean truth. One hallucinated fact — a wrong acquisition, a fake statistic, stale data — cascades through your entire pipeline.

AgentOracle sits between retrieval and action. It verifies every claim first.

---

## Install

```bash
pip install langchain-agentoracle
```

---

## Quickstart — gate your agent on verified claims

```python
from langchain_agentoracle import AgentOracleEvaluateTool

verifier = AgentOracleEvaluateTool()

agent_output = (
    "OpenAI released GPT-4 in March 2023. "
    "Bitcoin was invented by Elon Musk in 2009."
)

report = verifier._run(content=agent_output, min_confidence=0.8)
print(report)

if "[REFUTED]" in report:
    print("→ Hold — one or more claims failed verification")
else:
    print("→ Proceed")
```

That's it. Your agent now verifies before acting.

---

## Tools

| Tool | Endpoint | Cost |
|------|----------|------|
| `AgentOracleEvaluateTool` | `/evaluate` | $0.01 USDC per evaluation |
| `AgentOracleVerifyGateTool` | `/verify-gate` | Free (beta) |
| `AgentOraclePreviewTool` | `/preview` | Free, 10/hr |
| `AgentOracleResearchTool` | `/research` | $0.02 USDC |
| `AgentOracleDeepResearchTool` | `/deep-research` | $0.10 USDC (Sonar Pro) |
| `AgentOracleBatchResearchTool` | `/research/batch` | $0.02 USDC × N |

Bundle them all into an agent:

```python
from langchain_agentoracle import get_agentoracle_tools

tools = get_agentoracle_tools()                       # all 6 tools
tools = get_agentoracle_tools(include_paid=False)     # free tools only
```

---

## What `/evaluate` returns

```text
EVALUATION RESULT
Overall confidence: 0.51
Recommendation: ACT
Claims found: 3 | Supported: 2 | Refuted: 1 | Unverifiable: 0
Sources used: sonar, sonar-pro, adversarial, gemma-4

CLAIMS:
  ✓ [SUPPORTED] (1.00) OpenAI released GPT-4 in March 2023
  ✗ [REFUTED] (0.83) Bitcoin was invented by Elon Musk in 2009
     Correction: Bitcoin was invented by the pseudonymous Satoshi Nakamoto.
  ✓ [SUPPORTED] (1.00) The Eiffel Tower is located in Paris, France
```

---

## How it works

Every evaluation runs through 4 independent sources in parallel:

1. **Sonar** — real-time web research
2. **Sonar Pro** — deep multi-step analysis
3. **Adversarial** — actively tries to disprove the claim
4. **Gemma 4** — claim decomposition and confidence calibration

Consensus builds the score. Contradiction flags the risk.

---

## Try it free — no setup needed

```bash
curl -X POST https://agentoracle.co/preview \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenAI acquired Anthropic in 2026"}'
```

10 free previews per hour. No wallet, no API key, no account.

---

## Pricing

| Endpoint | Price |
|----------|-------|
| `/preview` | Free |
| `/verify-gate` | Free (beta) |
| `/evaluate` | $0.01 USDC per evaluation |
| `/research` | $0.02 USDC per query |
| `/deep-research` | $0.10 USDC per query |
| `/research/batch` | $0.02 USDC × N queries |

Payments via [x402 protocol](https://x402.org) — USDC on Base, SKALE (gasless), or Stellar. No subscriptions. No minimums. No API keys.

---

## Backwards compatibility

- `AgentOracleTool` (v0.1 name) is kept as an alias of `AgentOracleEvaluateTool`. Existing `from langchain_agentoracle import AgentOracleTool` code continues to work — calls are now routed through the full 4-source evaluation instead of the old preview wrapper.
- Error handling hardened in 0.2.1: 402 payment-required responses return structured x402 guidance, 429 returns `retry_after`, 500+ retries with exponential backoff, and `/evaluate` now defaults to a 120s timeout to accommodate multi-source tail latency.

---

## Related

- [agentoracle.co](https://agentoracle.co) — main site + live demo
- [Trust Layer docs](https://agentoracle.co/trust) — full API reference
- [crewai-agentoracle](https://github.com/TKCollective/crewai-agentoracle) — CrewAI integration
- [agentoracle-mcp](https://github.com/TKCollective/agentoracle-mcp) — MCP server for Claude, Cursor, Windsurf
- [x402 manifest](https://agentoracle.co/.well-known/x402.json) — agent-native pricing discovery

---

Built by [TK Collective](https://agentoracle.co) · x402 native · Base · SKALE · Stellar
