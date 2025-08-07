# postgres-assistant/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat
from app.agents.postgres_assistant_agent import get_agent_executor

# Create the main FastAPI application instance
app = FastAPI(
    title="Postgres Assistant API",
    description="An AI assistant for PostgreSQL powered by LangGraph and MCP.",
    version="1.0.0"
)

# --- CORS Middleware Setup ---
# This allows the frontend (running on a different domain/port) to make
# requests to this backend API. It's a crucial security feature for web apps.
origins = [
    "*",
    # "http://localhost:5173",  # Default port for Vite/React dev server
    # "http://127.0.0.1:5173",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all request headers
)

# --- Startup Event Handler ---
@app.on_event("startup")
async def startup_event():
    """
    This function is executed when the FastAPI application starts.
    It's the perfect place to initialize our agent, ensuring it's
    ready to handle requests without any delay on the first call.
    """
    print("--- Application Startup ---")
    await get_agent_executor()
    print("--- Application is now ready to accept requests ---")


# --- API Router Inclusion ---
# This includes all the routes defined in the chat.py module.
# The prefix ensures all these routes start with /api/v1.
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

# --- Root Endpoint ---
@app.get("/", tags=["Status"])
async def read_root():
    """
    A simple root endpoint to verify that the API server is running.
    """
    return {"status": "Postgres Assistant API is running"}