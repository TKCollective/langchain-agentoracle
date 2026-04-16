# AgentOracle for LangChain

> Stop your agent from acting on lies.

AgentOracle adds per-claim trust verification to any LangChain agent. 
Pass any content through `/evaluate` and get back confidence scores, 
verdicts, and a machine-readable recommendation — **ACT, VERIFY, or REJECT** 
— before your agent does anything with the data.

**$0.01 per claim. No API keys. x402 native on Base.**

---

## Why this exists

LangChain agents retrieve data and act on it. But retrieval doesn't mean 
truth. A single hallucinated fact — a wrong acquisition, a fake statistic, 
a stale price — can cascade through your entire pipeline.

AgentOracle sits between retrieval and action. It verifies first.

---

## Install

```bash
pip install langchain-agentoracle
```

---

## 30-Second Integration

```python
from langchain_agentoracle import AgentOracleTool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

# Add AgentOracle as a tool — that's it
tools = [AgentOracleTool()]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Your agent now verifies before acting
agent.run(
    "Research the latest AI agent frameworks and verify the claims before summarizing"
)
```

---

## What you get back

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

**Recommendations:**
| Score | Recommendation | What your agent should do |
|-------|---------------|--------------------------|
| > 0.8 | `act` | Proceed — claims verified |
| 0.5–0.8 | `verify` | Pause — route to human review |
| < 0.5 | `reject` | Discard — evidence insufficient |

---

## Try it free

No wallet. No setup. 20 free requests/hour.

```bash
curl -X POST https://agentoracle.co/preview \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenAI acquired Anthropic in 2026"}'
```

---

## Pricing

| Endpoint | Price | What it does |
|----------|-------|-------------|
| `/preview` | Free | Truncated results, no payment needed |
| `/evaluate` | $0.01/claim | Full verification, per-claim verdicts |
| `/research` | $0.02/query | Real-time research + verification |

Payments via [x402 protocol](https://x402.org) — USDC on Base. 
No subscriptions. No minimums.

---

## Links

- [Live Demo](https://agentoracle.co/preview)
- [Full Docs](https://agentoracle.co/trust)
- [MCP Server](https://github.com/TKCollective/agentoracle-mcp)
- [CrewAI Integration](https://github.com/TKCollective/crewai-agentoracle)
- [x402 Manifest](https://agentoracle.co/.well-known/x402.json)

---

Built by [TK Collective](https://agentoracle.co) · 
x402 native · Base · SKALE · Stellar
