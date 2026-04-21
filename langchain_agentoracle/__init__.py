"""LangChain integration for AgentOracle — trust verification tools for AI agents."""
from langchain_agentoracle.tools import (
    AgentOracleTool,  # legacy alias → AgentOracleEvaluateTool
    AgentOracleEvaluateTool,
    AgentOracleVerifyGateTool,
    AgentOraclePreviewTool,
    AgentOracleResearchTool,
    AgentOracleDeepResearchTool,
    AgentOracleBatchResearchTool,
    get_agentoracle_tools,
)

__all__ = [
    "AgentOracleTool",
    "AgentOracleEvaluateTool",
    "AgentOracleVerifyGateTool",
    "AgentOraclePreviewTool",
    "AgentOracleResearchTool",
    "AgentOracleDeepResearchTool",
    "AgentOracleBatchResearchTool",
    "get_agentoracle_tools",
]

__version__ = "0.2.1"
