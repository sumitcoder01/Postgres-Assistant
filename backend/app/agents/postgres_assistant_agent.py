# postgres-assistant/backend/app/agents/postgres_assistant_agent.py

import asyncio
import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.core.settings import settings
from app.services.llm_service import get_llm

# --- Agent State ---
# We define a global variable to hold the agent executor.
# This is a common pattern to ensure the agent is initialized only once
# when the application starts, improving performance.
agent_executor = None

async def create_agent():
    """
    An asynchronous function to initialize and return the LangGraph agent.

    This function performs the following steps:
    1.  Locates the MCP configuration file.
    2.  Initializes the MultiServerMCPClient, which will start and manage the
        `crystaldba/postgres-mcp` Docker container in the background.
    3.  Dynamically fetches the available tools from the running MCP server.
    4.  Retrieves the configured LLM using the llm_service.
    5.  Sets up a checkpointer using SQLite for short-term conversational memory.
    6.  Builds the final ReAct agent by combining the LLM, tools, and memory.

    Returns:
        A compiled LangGraph agent executor, ready to process requests.
    """
    print("🤖 Initializing Postgres Assistant Agent...")

    # 1. Define the path and read the base MCP configuration file.
    config_path = Path(__file__).parents[2] / "config" / "mcp_config.json"
    print(f"🔧 Loading MCP config from: {config_path}")
    with open(config_path, 'r') as f:
        config_template = f.read()

    # 2. Inject the database URI into the configuration string.
    config_string = config_template.replace("${input:pg_url}", settings.POSTGRES_URI)
    mcp_config_data = json.loads(config_string)
    print("🔧 Database URI injected into MCP configuration.")

    # 3. Initialize the MCP client directly with the config dictionary.
    mcp_client = MultiServerMCPClient(mcp_config_data["mcpServers"])

    # 4. Dynamically get the tools from the MCP server.
    tools = await mcp_client.get_tools()
    print(f"🛠️  Tools loaded successfully: {[tool.name for tool in tools]}")

    llm = get_llm()
    print(f"🧠 LLM Provider configured: {settings.LLM_PROVIDER.upper()}")

   
    system_prompt = (
        "You are a helpful and expert PostgreSQL assistant. "
        "Your primary role is to help users by answering their questions about the database.\n"
        "To do this, you have access to a set of powerful tools:\n"
        "- `sql_db_query`: To run SQL queries.\n"
        "- `sql_db_schema`: To inspect the schema of specific tables.\n"
        "- `sql_db_list_tables`: To list all tables in the database.\n\n"
        "Your workflow should be:\n"
        "1. First, use `sql_db_list_tables` to see what tables are available.\n"
        "2. Then, use `sql_db_schema` on the most relevant tables to understand their columns.\n"
        "3. Finally, construct a SQL query using `sql_db_query` to answer the user's question.\n"
        "Summarize the final result in a clear and easy-to-understand way."
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    
    agent = create_react_agent(model=llm, tools=tools, prompt=prompt)
    print("✅ Agent created and compiled successfully.")
    
    return agent

async def get_agent_executor():
    """
    Gets the singleton instance of the agent executor.

    If the agent hasn't been initialized yet, it calls the creation
    function. This ensures the agent is only created once.
    """
    global agent_executor
    if agent_executor is None:
        agent_executor = await create_agent()
    return agent_executor
