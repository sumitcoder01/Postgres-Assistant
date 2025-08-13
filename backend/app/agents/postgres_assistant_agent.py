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

    # 5. Fetch the database schema resources from the MCP server.
    print("📄 Fetching database schema resources...")
    # The server_name must match the key used in your mcp_config.json's "servers" block.
    resources = await mcp_client.get_resources(server_name="postgres")
    
    schema_descriptions = []
    for resource in resources:
        try:
            # 1. Get the URI from the metadata and the table name from the URI
            uri_str = str(resource.metadata['uri'])
            table_name = uri_str.split('/')[-2]

            # 2. **THE FIX**: resource.data is a JSON STRING. Parse it with json.loads().
            schema_json_string = resource.data
            columns_data = json.loads(schema_json_string)
            
            # 3. Now that columns_data is a proper list of dictionaries, format it
            column_defs = [f"- {col['column_name']} ({col['data_type']})" for col in columns_data]

            # 4. Combine and append the full table description
            full_table_description = f"Table `{table_name}`:\n" + "\n".join(column_defs)
            schema_descriptions.append(full_table_description)
            
        except Exception as e:
            uri_for_error = str(resource.metadata.get('uri', 'unknown')) if hasattr(resource, 'metadata') else 'unknown'
            print(f"⚠️ Could not parse schema for resource '{uri_for_error}': {e}")
            
    # --- END OF SCHEMA PARSING ---

    # --- Final Prompt Assembly ---
    database_schema_string = "\n\n".join(schema_descriptions)
    if not database_schema_string:
        print("⚠️ Warning: No database schema information was loaded.")
        database_schema_string = "No schema information is available to the agent."
    else:
        print("✅ Database schema loaded successfully. Passing to agent.")
        print("--- SCHEMA FOR AGENT ---")
        print(database_schema_string)
        print("------------------------")


    # 6. Get the configured LLM instance.
    llm = get_llm()
    print(f"🧠 LLM Provider configured: {settings.LLM_PROVIDER.upper()}")
    database_schema_string = ""
    system_prompt = (
        "You are a helpful and expert PostgreSQL assistant. "
        "Your role is to help users analyze and optimize their database by writing and executing `query` tools. "
        "You MUST use the provided database schema below to write accurate SQL queries. "
        "When you use a tool, briefly inform the user what you are doing. "
        "After you get the result from a tool, summarize it in a clear, easy-to-understand way. "
        "Be polite and concise."
        "\n\n--- DATABASE SCHEMA ---\n"
        f"{database_schema_string}"
        "\n--- END SCHEMA ---"
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
