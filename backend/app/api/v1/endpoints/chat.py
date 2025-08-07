# postgres-assistant/backend/app/api/v1/endpoints/chat.py

import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.agents.postgres_assistant_agent import get_agent_executor

# Create an APIRouter. This allows us to organize routes in a modular way.
# The main application will include this router.
router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: Request):
    """
    Handles a streaming chat request with the Postgres Assistant agent.

    This endpoint receives a user's query and a unique thread_id to maintain
    conversation context. It then uses the pre-initialized LangGraph agent
    to process the query and streams the response back to the client in real-time
    using Server-Sent Events (SSE).

    The streamed events include:
    - 'token': Individual text chunks from the LLM.
    - 'tool_start': Information about which tool the agent is about to use.
    - 'tool_end': The result from the tool execution.
    - 'stream_end': A final message to signal the end of the response.
    - 'error': Any errors that occur during the process.
    """
    try:
        body = await request.json()
        user_query = body.get("query")
        # thread_id is crucial for LangGraph's checkpointer to maintain memory
        thread_id = body.get("thread_id")

        if not user_query or not thread_id:
            raise HTTPException(
                status_code=400, 
                detail="Request body must include 'query' and 'thread_id'."
            )

        # Get the singleton agent instance
        agent = await get_agent_executor()
        
        # The config dictionary tells LangGraph which conversation thread to use or create
        config = {"configurable": {"thread_id": thread_id}}
        
        # The input to the agent is always a list of messages
        messages = [HumanMessage(content=user_query)]

        async def event_stream():
            """
            A generator function that yields Server-Sent Events.
            It asynchronously iterates through the agent's event stream.
            """
            try:
                # astream_events provides a detailed stream of the graph's execution
                async for event in agent.astream_events(messages, config, version="v2"):
                    kind = event["event"]
                    
                    if kind == "on_chat_model_stream":
                        content = event["data"]["chunk"].content
                        if content:
                            yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                    elif kind == "on_tool_start":
                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name'], 'input': event['data'].get('input')})}\n\n"
                    elif kind == "on_tool_end":
                        yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name'], 'output': event['data'].get('output')})}\n\n"
                
                yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

            except Exception as e:
                error_message = f"An error occurred during agent execution: {e}"
                yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in request body.")
    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=str(e))