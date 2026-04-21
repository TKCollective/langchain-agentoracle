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

verifier = AgentOracleEvaluateTool(min_confidence=0.8)

agent_output = (
    "OpenAI released GPT-4 in March 2023. "
    "Bitcoin was invented by Elon Musk in 2009."
)

report = verifier._run(content=agent_output)
print(report)

if "[REFUTED]" in report:
    print("→ Hold — one or more claims failed verification")
else:
    print("→ Proceed")
```

That's it. Your agent now verifies before acting.

---

## Tools

| Tool | What it does | Cost |
|------|--------------|------|
| `AgentOracleEvaluateTool` | Per-claim verification — verdicts, confidence, evidence, corrections | $0.02 USDC (free in beta) |
| `AgentOracleVerifyGateTool` | Fast PASS/FAIL binary gate | Free (beta) |
| `AgentOraclePreviewTool` | Free truncated research preview, 10/hr | Free |
| `AgentOracleResearchTool` | Full research with sources | $0.02 USDC |

Bundle them all into an agent:

```python
from langchain_agentoracle import get_agentoracle_tools

tools = get_agentoracle_tools()          # free + verify tools
tools = get_agentoracle_tools(include_paid=True)  # add /research
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

| Endpoint | Price | What it does |
|----------|-------|-------------|
| `/preview` | Free | Truncated results, no payment needed |
| `/verify-gate` | Free (beta) | Fast pass/fail confidence gate |
| `/evaluate` | $0.02 USDC | Per-claim verification + verdicts |
| `/research` | $0.02 USDC | Real-time research + verification |

Payments via [x402 protocol](https://x402.org) — USDC on Base, SKALE (gasless), or Stellar. No subscriptions. No minimums. No API keys.

---

## Compatibility

- `AgentOracleTool` (v0.1 name) is kept as an alias of `AgentOraclePreviewTool` for backwards compatibility. New code should use the named tools above.

---

## Related

- [agentoracle.co](https://agentoracle.co) — main site + live demo
- [Trust Layer docs](https://agentoracle.co/trust) — full API reference
- [crewai-agentoracle](https://github.com/TKCollective/crewai-agentoracle) — CrewAI integration
- [agentoracle-mcp](https://github.com/TKCollective/agentoracle-mcp) — MCP server for Claude, Cursor, Windsurf
- [x402 manifest](https://agentoracle.co/.well-known/x402.json) — agent-native pricing discovery

---

Built by [TK Collective](https://agentoracle.co) · x402 native · Base · SKALE · Stellar
