# postgres-assistant/backend/app/api/v1/endpoints/chat.py

import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from app.workflow.graph import get_graph_executor

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: Request):
    """
    Handles a streaming chat request with the Postgres Assistant agent.

    This endpoint receives a user's query and a unique thread_id to maintain
    conversation context. It uses the pre-initialized LangGraph agent
    to process the query and streams the response back to the client in real-time
    using Server-Sent Events (SSE).
    """
    try:
        body = await request.json()
        user_query = body.get("query")
        thread_id = body.get("thread_id")

        if not user_query or not thread_id:
            raise HTTPException(
                status_code=400, 
                detail="Request body must include 'query' and 'thread_id'."
            )

        config = {"configurable": {"thread_id": thread_id}}
        messages = [HumanMessage(content=user_query)]
        super_graph = await get_graph_executor()
        async def event_stream():
            try:
                async for event in super_graph.astream_events( {"messages": messages } , config):
                    kind = event.get("event")

                    if kind == "on_chat_model_stream":
                        chunk = event["data"].get("chunk")  # Get the AIMessageChunk object
                        if chunk:
                            content = chunk.content         # Access its .content attribute
                            if content:
                                # Yield the content if it's not empty
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

                    elif kind == "on_tool_start":
                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event.get('name'), 'input': event['data'].get('input')})}\n\n"

                    elif kind == "on_tool_end":
                        yield f"data: {json.dumps({'type': 'tool_end', 'tool': event.get('name'), 'output': event['data'].get('output')})}\n\n"

                yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

            except Exception as e:
                error_message = f"Agent execution error: {str(e)}"
                yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in request body.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")