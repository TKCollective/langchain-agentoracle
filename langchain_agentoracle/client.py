from __future__ import annotations
import httpx

PREVIEW_ENDPOINT = "https://agentoracle.co/preview"

class AgentOracleClient:
    def __init__(self):
        self._http = httpx.Client(timeout=10.0)

    def query(self, question: str) -> dict:
        resp = self._http.post(PREVIEW_ENDPOINT, json={"query": question})
        resp.raise_for_status()
        data = resp.json()
        data["preview"] = True
        return data
