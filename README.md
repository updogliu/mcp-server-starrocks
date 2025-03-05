# Starrocks Official MCP server


## Components

### Tools

* `read_query`
  - Execute a SELECT query or commands that return a ResultSet

* `write_query`
  - Execute an DDL/DML or other StarRocks command that do not have a ResultSet

### Configuration

mcp server config

```json
{
  "mcpServers": {
    "mcp-server-starrocks": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp-server-starrocks",
        "mcp-server-starrocks"
      ],
      "env": {
        "STARROCKS_HOST": "default localhost",
        "STARROCKS_PORT": "default 9030",
        "STARROCKS_USER": "default root",
        "STARROCKS_PASSWORD": "default empty"
      }
    }
  }
}
```


### Resources

TODO

### Prompts

TODO
