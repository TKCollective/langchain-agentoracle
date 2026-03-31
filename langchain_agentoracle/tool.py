from __future__ import annotations
from .client import AgentOracleClient

class AgentOracleTool:
    name = "agentoracle_research"
    description = "Research questions using AgentOracle"

    def __init__(self):
        self._client = AgentOracleClient()

    def invoke(self, data: dict) -> str:
        query = data["query"]
        result = self._client.query(query)
        return str(result)

    def run(self, query: str) -> str:
        result = self._client.query(query)
        return str(result)
