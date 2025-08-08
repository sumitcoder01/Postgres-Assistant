from app.workflow.state import State
from langgraph.graph import StateGraph , END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.postgres_assistant_agent import get_agent_executor

super_graph = None

async def build_graph():
    workflow = StateGraph(State)
    # Set up the checkpointer for persistent memory.
    memory = MemorySaver()
    print("📝 Short-term memory (checkpointer) enabled using In-Memory Saver.")

    postgres_agent = await get_agent_executor()
    workflow.add_node("postgres-agent", postgres_agent)
    workflow.set_entry_point("postgres-agent")
    workflow.add_edge("postgres-agent" , END)
    graph = workflow.compile(checkpointer=memory)
    return graph

async def get_graph_executor():
    """
    Returns the singleton instance of the compiled graph executor.
    Initializes it if it doesn't exist.
    """
    global super_graph
    if super_graph is None:
        super_graph = await build_graph()
    return super_graph
    


