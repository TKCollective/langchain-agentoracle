from langchain_agentoracle import AgentOracleTool

tool = AgentOracleTool()

result = tool.invoke({
    "query": "What are the latest developments in AI agent frameworks?"
})

print(result)
