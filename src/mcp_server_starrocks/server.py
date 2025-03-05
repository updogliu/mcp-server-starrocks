import os
import io
import time
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
import mysql.connector


SERVER_VERSION = "0.1.0"

server = Server("mcp-server-starrocks", SERVER_VERSION)

global_connection = None


def get_connection():
    global global_connection
    if global_connection is None:
        global_connection = mysql.connector.connect(
            host=os.getenv('STARROCKS_HOST', 'localhost'),
            port=os.getenv('STARROCKS_PORT', '9030'),
            user=os.getenv('STARROCKS_USER', 'root'),
            password=os.getenv('STARROCKS_PASSWORD', '')
        )
    return global_connection


def reset_connection():
    global global_connection
    if global_connection is not None:
        global_connection.close()
        global_connection = None


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return []


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return []


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    raise ValueError(f"Unsupported get_prompt")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_query",
            description="Execute a SELECT query or commands that return a ResultSet",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="write_query",
            description="Execute an DDL/DML or other StarRocks command that do not have a ResultSet",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL to execute"},
                },
                "required": ["query"],
            },
        ),
    ]


def handle_read_query(conn, query):
    # return csv like result set, with column names as first row
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]  # Get column names
        rows = cursor.fetchall()

        output = io.StringIO()

        # Convert rows to CSV-like format
        def to_csv_line(row):
            return ",".join(
                str(item).replace("\"", "\"\"") if isinstance(item, str) else str(item) for item in row)

        output.write(to_csv_line(columns) + "\n")  # Write column names
        for row in rows:
            output.write(to_csv_line(row) + "\n")  # Write data rows

        output.write(f"\n{len(rows)} rows in set\n")
        return output.getvalue()
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()


def handle_write_query(conn, query):
    cursor = conn.cursor()
    start_time = time.time()
    try:
        cursor.execute(query)
        affected_rows = cursor.rowcount
        elapsed_time = time.time() - start_time
        return f"{affected_rows} rows affected ({elapsed_time:.2f} sec)"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        cursor.close()


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    try:
        conn = get_connection()
        if name == "read_query":
            return [types.TextContent(type="text", text=handle_read_query(conn, arguments["query"]))]
        if name == "write_query":
            return [types.TextContent(type="text", text=handle_write_query(conn, arguments["query"]))]
    except Exception as e:
        reset_connection()
        return [types.TextContent(type="text", text=str(e))]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-starrocks",
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
