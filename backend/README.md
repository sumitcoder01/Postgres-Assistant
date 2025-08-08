<div align="center">

🤖 Postgres Assistant - Backend 🐘
An intelligent, conversational AI designed to help you analyze, optimize, and manage your PostgreSQL database through natural language.

</div>

<p align="center">
<img alt="Python Version" src="https://www.google.com/search?q=https://img.shields.io/badge/python-3.10%2B-blue.svg">
<img alt="Framework" src="https://www.google.com/search?q=https://img.shields.io/badge/framework-FastAPI-05998b.svg">
<img alt="LangGraph" src="https://www.google.com/search?q=https://img.shields.io/badge/engine-LangGraph-f472b6.svg">
<img alt="License" src="https://www.google.com/search?q=https://img.shields.io/badge/license-MIT-green.svg">
</p>

This backend server is the core of the Postgres Assistant. It uses FastAPI to expose a streaming API and leverages the power of LangGraph to create a reasoning agent. This agent can dynamically use tools from a Postgres MCP (Model Context Protocol) server to perform complex database tasks based on your requests.

✨ Core Features
🧠 Intelligent Agent: Powered by LangGraph's ReAct (Reasoning and Acting) framework to understand intent and use tools.

🔧 Dynamic Tool Integration: Automatically loads and uses database tools (like health checks and query analysis) from a crystaldba/postgres-mcp server.

🔄 Multi-LLM Support: Flexibly switch between top LLM providers (OpenAI, Gemini, Anthropic, Groq, etc.) via a single environment variable.

📝 Conversational Memory: Remembers the context of your current conversation using a built-in SQLite checkpointer for seamless interaction.

⚡ Real-time Streaming: Utilizes Server-Sent Events (SSE) to stream the agent's thoughts and responses token-by-token for a highly responsive UI.

🐳 Fully Dockerized: Comes with Dockerfile and docker-compose.yml for easy, consistent deployment in any environment.

🏗️ Modular & Scalable: Built with a professional, modular structure that's easy to maintain, test, and extend.

⚙️ How It Works
The application follows a clean, decoupled architecture. A user's request flows through the system to get an intelligent, context-aware response.

graph TD
    A[User via Frontend] -->|HTTP Request| B(FastAPI Backend);
    B -->|Process Query| C{LangGraph Agent};
    C -->|Selects & Uses Tool| D[Postgres MCP Server];
    D -->|Executes on DB| E[(PostgreSQL Database)];
    E -->|Returns Data| D;
    D -->|Returns Tool Output| C;
    C -->|Generates Response| B;
    B -->|SSE Stream| A;

🚀 Getting Started
You can run the backend server either directly on your local machine or using Docker.
  # On Windows, use `venv\Scripts\activate`

Prerequisites
Python (v3.10 or newer)

Docker and Docker Compose

Git

Option 1: Running Locally
This is great for development and making code changes.

1. Clone the Repository

git clone [https://github.com/sumitcoder01/Postgres-Assistant.git](https://github.com/sumitcoder01/Postgres-Assistant.git)
cd Postgres-Assistant/backend

2. Configure Environment Variables
Copy the example .env.example file to a new .env file and fill in your details.

cp .env.example .env

Now, edit the .env file with your text editor:

POSTGRES_URI: The full connection string for your PostgreSQL database.

LLM_PROVIDER: The AI provider you wish to use (e.g., openai).

OPENAI_API_KEY, etc.: The API key for your chosen provider.

3. Install Dependencies
It's highly recommended to use a Python virtual environment.

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate
# Install the packages
pip install -r requirements.txt

4. Run the Application
Start the FastAPI server with Uvicorn.

uvicorn main:app --reload

The server will be available at http://localhost:8000. You can view the interactive API docs at http://localhost:8000/docs.

Option 2: Running with Docker (Recommended)
This is the easiest way to get started, as it handles all dependencies and setup within isolated containers.

1. Pull the MCP Server Image (Optional)

You can pre-pull the Postgres MCP Pro server image from Docker Hub. This step is optional, as docker-compose will do it for you, but it's good practice. This image contains all necessary dependencies for running the database analysis tools.

docker pull crystaldba/postgres-mcp

2. Clone & Configure

If you haven't already, clone the repository and create your .env file by copying .env.example. Make sure to fill in your POSTGRES_URI and LLM_PROVIDER details.

3. Build and Run with Docker Compose

From the backend directory, run the following command:

docker-compose up --build

Docker will build the backend image and start all the necessary services. The API will then be available at http://localhost:8000.

⚡ API Usage Example
You can test the streaming API using a curl command. Make sure to provide a query and a unique thread_id for conversation tracking.

curl -X POST http://localhost:8000/api/v1/chat/stream \
-H "Content-Type: application/json" \
-N \
-d '{
    "query": "Analyze the health of my database and list any potential issues.",
    "thread_id": "user-123-thread-abc"
}'

Note: The -N flag disables buffering in curl, allowing you to see the stream in real-time.

You will see a stream of Server-Sent Events in your terminal as the agent thinks and responds.

🤝 Contributing
Contributions are welcome! Whether it's adding a new feature, improving documentation, or fixing a bug, please feel free to open an issue or submit a pull request.

Fork the repository.

Create a new branch (git checkout -b feature/your-feature-name).

Commit your changes (git commit -m 'Add some amazing feature').

Push to the branch (git push origin feature/your-feature-name).

Open a Pull Request.

📜 License
This project is licensed