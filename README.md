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

## Quickstart

```python
from langchain_agentoracle import AgentOracleTool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

tools = [AgentOracleTool()]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

agent.run(
    "Research the latest AI agent frameworks and verify the claims before summarizing"
)
```

That's it. Your agent now verifies before acting.

---

## What comes back

```json
{
  "overall_confidence": 0.87,
  "recommendation": "act",
  "claims": [
    {
      "claim": "LangGraph leads agent frameworks in 2026",
      "verdict": "supported",
      "confidence": 0.94,
      "evidence": "Confirmed across 4 independent sources"
    },
    {
      "claim": "OpenAI acquired Anthropic in early 2026",
      "verdict": "refuted",
      "confidence": 0.04,
      "correction": "Anthropic remains independent as of April 2026"
    }
  ]
}
```

---

## Recommendation logic

| Score | Recommendation | What your agent should do |
|-------|---------------|--------------------------|
| > 0.8 | `act` | Proceed — claims verified |
| 0.5–0.8 | `verify` | Pause — needs secondary check |
| < 0.5 | `reject` | Discard — evidence insufficient |

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

20 free requests per hour. No wallet, no API key, no account.

---

## Pricing

| Endpoint | Price | What it does |
|----------|-------|-------------|
| `/preview` | Free | Truncated results, no payment needed |
| `/evaluate` | $0.01/claim | Full per-claim verification + verdicts |
| `/research` | $0.02/query | Real-time research + verification |

Payments via [x402 protocol](https://x402.org) — USDC on Base, SKALE (gasless), or Stellar. No subscriptions. No minimums. No API keys.

---

## Related

- [agentoracle.co](https://agentoracle.co) — main site + live demo
- [Trust Layer docs](https://agentoracle.co/trust) — full API reference
- [crewai-agentoracle](https://github.com/TKCollective/crewai-agentoracle) — CrewAI integration
- [agentoracle-mcp](https://github.com/TKCollective/agentoracle-mcp) — MCP server for Claude, Cursor, Windsurf
- [x402 manifest](https://agentoracle.co/.well-known/x402.json) — agent-native pricing discovery

---

Built by [TK Collective](https://agentoracle.co) · x402 native · Base · SKALE · Stellar
