import sys
import os
import asyncio
import json
from typing import List, Dict, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastmcp import FastMCP
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import BaseTool
from app.services.llm_service import get_llm

# Initialize the FastMCP Server
mcp = FastMCP("LangChain SQL Toolkit Server")

# Global variables to store database connection
_database = None
_toolkit = None

def initialize_database(db_uri: str):
    """Initialize the database connection and toolkit."""
    global _database, _toolkit
    
    print(f"MCP Server: Initializing database connection from URI...", flush=True)
    _database = SQLDatabase.from_uri(db_uri)
    
    print("MCP Server: Initializing LLM for toolkit...", flush=True)
    llm = get_llm()
    
    _toolkit = SQLDatabaseToolkit(db=_database, llm=llm)
    print("MCP Server: Database and toolkit initialized successfully", flush=True)

@mcp.tool(name="sql_db_query", description="Execute a SQL query against the database and return results. Use this to run SELECT, INSERT, UPDATE, or other SQL commands.")
async def sql_db_query(query: str) -> str:
    """Execute a SQL query against the database"""
    try:
        if _database is None:
            return "Error: Database not initialized"
        
        print(f"MCP Server: Executing query: {query[:100]}...", flush=True)
        
        # Use the database directly for better control
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _database.run(query))
        
        # Format the result nicely
        if isinstance(result, list):
            if len(result) == 0:
                return "Query executed successfully. No rows returned."
            elif len(result) > 100:
                return f"Query returned {len(result)} rows. First 100 rows:\n{str(result[:100])}"
            else:
                return f"Query returned {len(result)} rows:\n{str(result)}"
        else:
            return str(result)
            
    except Exception as e:
        error_msg = f"Error executing SQL query: {str(e)}"
        print(f"MCP Server: {error_msg}", flush=True)
        return error_msg

@mcp.tool(name="sql_db_schema", description="Get the schema and table information for the database. Optionally specify table names separated by commas.")
async def sql_db_schema(table_names: Optional[str] = None) -> str:
    """Get schema information for database tables"""
    try:
        if _database is None:
            return "Error: Database not initialized"
        
        print(f"MCP Server: Getting schema for tables: {table_names or 'all'}", flush=True)
        
        loop = asyncio.get_event_loop()
        if table_names and table_names.strip():
            # Get schema for specific tables
            table_list = [t.strip() for t in table_names.split(',')]
            result = await loop.run_in_executor(None, lambda: _database.get_table_info(table_list))
        else:
            # Get schema for all tables
            result = await loop.run_in_executor(None, lambda: _database.get_table_info())
        
        return str(result)
        
    except Exception as e:
        error_msg = f"Error getting schema: {str(e)}"
        print(f"MCP Server: {error_msg}", flush=True)
        return error_msg

@mcp.tool(name="sql_db_list_tables", description="List all available tables in the database")
async def sql_db_list_tables() -> str:
    """List all tables in the database"""
    try:
        if _database is None:
            return "Error: Database not initialized"
        
        print("MCP Server: Listing all tables", flush=True)
        
        loop = asyncio.get_event_loop()
        tables = await loop.run_in_executor(None, lambda: _database.get_usable_table_names())
        
        if isinstance(tables, list):
            return f"Available tables ({len(tables)}): {', '.join(tables)}"
        else:
            return f"Available tables: {str(tables)}"
            
    except Exception as e:
        error_msg = f"Error listing tables: {str(e)}"
        print(f"MCP Server: {error_msg}", flush=True)
        return error_msg

@mcp.tool(name="sql_db_query_checker", description="Check if a SQL query is safe and valid before execution")
async def sql_db_query_checker(query: str) -> str:
    """Validate a SQL query for safety and syntax"""
    try:
        if _database is None:
            return "Error: Database not initialized"
        
        print(f"MCP Server: Checking query safety: {query[:50]}...", flush=True)
        
        # Basic safety checks
        query_upper = query.strip().upper()
        
        # Check for dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER TABLE', 'CREATE DATABASE', 'DROP DATABASE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return f"WARNING: Query contains potentially dangerous keyword '{keyword}'. Please review carefully."
        
        # Check for basic syntax issues
        if not query.strip():
            return "ERROR: Empty query provided"
        
        if not query.strip().endswith(';') and query_upper.startswith('SELECT'):
            query += ';'
        
        # Try to validate with a dry run (using EXPLAIN for SELECT queries)
        if query_upper.startswith('SELECT'):
            try:
                loop = asyncio.get_event_loop()
                explain_query = f"EXPLAIN {query}"
                await loop.run_in_executor(None, lambda: _database.run(explain_query))
                return "Query syntax appears valid and safe for execution"
            except Exception as syntax_error:
                return f"Query syntax error: {str(syntax_error)}"
        
        return "Query passed basic safety checks. Please review before execution."
        
    except Exception as e:
        error_msg = f"Error checking query: {str(e)}"
        print(f"MCP Server: {error_msg}", flush=True)
        return error_msg

@mcp.tool(name="sql_db_info", description="Get general information about the database connection and capabilities")
async def sql_db_info() -> str:
    """Get information about the database"""
    try:
        if _database is None:
            return "Error: Database not initialized"
        
        print("MCP Server: Getting database info", flush=True)
        
        loop = asyncio.get_event_loop()
        
        # Get basic database info
        tables = await loop.run_in_executor(None, lambda: _database.get_usable_table_names())
        dialect = str(_database.dialect)
        
        info = {
            "dialect": dialect,
            "total_tables": len(tables) if isinstance(tables, list) else "Unknown",
            "table_names": tables[:10] if isinstance(tables, list) and len(tables) > 10 else tables,
            "connection_status": "Connected"
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        error_msg = f"Error getting database info: {str(e)}"
        print(f"MCP Server: {error_msg}", flush=True)
        return error_msg

@mcp.tool(name="health_check", description="Check if the MCP server and database connection are working correctly")
async def health_check() -> str:
    """Check server and database health status"""
    try:
        status = {
            "server_status": "running",
            "database_initialized": _database is not None,
            "toolkit_initialized": _toolkit is not None
        }
        
        if _database is not None:
            try:
                # Test database connection with a simple query
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: _database.run("SELECT 1"))
                status["database_connection"] = "active"
            except Exception as db_error:
                status["database_connection"] = f"error: {str(db_error)}"
        else:
            status["database_connection"] = "not_initialized"
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return f"Health check error: {str(e)}"

@mcp.tool(name="list_available_tools", description="List all available SQL tools and their descriptions")
async def list_available_tools() -> str:
    """List all available tools with descriptions"""
    tools_info = [
        "🔍 sql_db_query - Execute SQL queries (SELECT, INSERT, UPDATE, etc.)",
        "📋 sql_db_schema - Get table schema and structure information", 
        "📊 sql_db_list_tables - List all available database tables",
        "✅ sql_db_query_checker - Validate SQL queries for safety and syntax",
        "ℹ️ sql_db_info - Get database connection and general information",
        "❤️ health_check - Check server and database health status",
        "📝 list_available_tools - Show this tool list"
    ]
    return "\n".join(tools_info)

def main():
    """Main function to initialize and run the MCP server"""
    if len(sys.argv) < 2:
        print("FATAL: Database URI not provided as a command-line argument.", file=sys.stderr)
        print("Usage: python sql_mcp_server.py <database_uri>", file=sys.stderr)
        sys.exit(1)
        
    database_url = sys.argv[-1]
    print(f"MCP Server: Using database URI: {database_url[:50]}...", flush=True)
    
    try:
        # Initialize database connection
        initialize_database(database_url)
        print("MCP Server: SQL tools initialized successfully", flush=True)
        
    except Exception as e:
        import traceback
        print(f"FATAL: Failed to initialize database connection. Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Print startup confirmation
    print("MCP Server: All tools registered and ready", flush=True)
    print("MCP Server: Starting stdio transport...", flush=True)
    
    try:
        # Run the server with stdio transport
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nMCP Server: Shutting down gracefully...", flush=True)
    except Exception as e:
        print(f"MCP Server: Runtime error: {e}", file=sys.stderr)
        sys.exit(1)

# Main execution block
if __name__ == "__main__":
    main()